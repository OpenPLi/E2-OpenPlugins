#include <iostream>
#include <fstream>
#include <vector>
#include <math.h>
#include <strings.h>
#include <unistd.h>

bool FanOK = false;
int maxRPM = 0;
int minPWM = 0;
enum fantype {TYPE_PWM = 0, TYPE_VOLTAGE = 1} FanType;

int clamp(int val, int min, int max)
{
	if (val < min) return min;
	if (val > max) return max;
	return val;
}

int skal(int x, int x1, int x2, int y1, int y2)
{
	if (x > x2) return y2;
	if (x < x1) return y1;
	int m = (y2 - y1) / (x2 - x1);
	int y = m * x + y1;
	return y;
}

void FanParameter()
{
	{
		std::ofstream vlt("/proc/stb/fp/fan_vlt");
		vlt << "ff";
	}
	{
		std::ofstream pwm("/proc/stb/fp/fan_pwm");
		pwm << "ff";
	}
	sleep(5);
	{
		std::ifstream speed("/proc/stb/fp/fan_speed");
		speed >> maxRPM;
	}

	if (!maxRPM)
	{
		FanOK = false;
		{
			std::ofstream vlt("/proc/stb/fp/fan_vlt");
			vlt << "00";
		}
		{
			std::ofstream pwm("/proc/stb/fp/fan_pwm");
			pwm << "00";
		}
		return;
	}
	else
	{
		FanOK = true;
	}

	{
		std::ofstream pwm("/proc/stb/fp/fan_pwm");
		pwm << "00";
	}

	sleep(5);
	{
		std::ifstream speed("/proc/stb/fp/fan_speed");
		speed >> minPWM;
	}
	if (minPWM < (maxRPM * 8 / 10))
	{
		FanType = TYPE_PWM;
	}
	else
	{
		FanType = TYPE_VOLTAGE;
	}
}

class TemperatureSensor
{
public:
	virtual int readTemp() = 0;
};

class FPTemperature : public TemperatureSensor
{
	int index;
public:
	FPTemperature(int id) : index(id) {}
	int readTemp()
	{
		char name[512];
		sprintf(name, "/proc/stb/fp/temp%d", index);
		std::ifstream file(name);
		double t;
		file >> t;
		t = t / 256.0 * 3.3;
		t = 4.246 * exp(1.0) * t + 7.362 * exp(-1.0);
		return (int)t;
	}
};

class FanControl
{
public:
	virtual int getRPM() = 0;
	virtual void setOutput(int) = 0;
};

class FPFanControl : public FanControl
{
	bool zeroRPM;
	fantype ourType;
public:
	FPFanControl(fantype type)
	{
		zeroRPM = false;
		ourType = type;
		if (ourType == TYPE_PWM)
		{
			std::ofstream vlt("/proc/stb/fp/fan_vlt");
			vlt << "ff";
		}
		else
		{
			std::ofstream pwm("/proc/stb/fp/fan_pwm");
			pwm << "ff";
		}
	}

	void setOutput(int output)
	{
		char value[15];
		sprintf(value, "%x", output);
		if (ourType == TYPE_PWM)
		{
			std::ofstream pwm("/proc/stb/fp/fan_pwm");
			pwm << value;
		}
		else
		{
			std::ofstream vlt("/proc/stb/fp/fan_vlt");
			vlt << value;
		}
	}

	int getRPM()
	{
		int rpm;
		std::ifstream speed("/proc/stb/fp/fan_speed");
		speed >> rpm;
		return rpm;
	}
};

class PID
{
	double Kp, Ki, Kd;
	double i, prev;
public:
	PID(double Kp = 1.0/100.0, double Ki = 1.0/100.0, double Kd = 0.0)
	{
		this->Kp = Kp;
		this->Ki = Ki;
		this->Kd = Kd;
		i = 0;
		prev = 0;
	}

	int cycle(double current, double target, double dT = 1.0)
	{
		double error = target - current;
		i += error * dT;
		double deriv = (error - prev) / dT;
		double out = Kp * error + Ki * i + Kd * deriv;
		prev = error;
		return (int)out;
	}
};

class FanLoopPID
{
	FanControl *fan;
	PID pid;

public:
	int target_rpm;
	
public:
	FanLoopPID(FanControl *fan)
	{
		this->fan = fan;
		target_rpm = 1000;
	}

	void cycle(double dT = 1.0)
	{
		int cur_rpm = fan->getRPM();
		int out = pid.cycle(cur_rpm, target_rpm, dT);
		fan->setOutput(clamp(out, 0, 255));
	}
};

class TemperatureLoop
{
public:
	int FAN_MIN;
	int FAN_MAX;
	int target_temp;
	int Range;
	int maxTemp;
	bool noLED, noALERT;

protected:
	bool Alert;
	std::vector<TemperatureSensor *> &sensors;

	int readCurrentTemperature()
	{
		int maxtemp = 0;
		for (unsigned int i = 0; i < sensors.size(); i++)
		{
			int temp = sensors[i]->readTemp();
			if (temp > maxtemp) maxtemp = temp;
		}
		return maxtemp;
	}
public:
	TemperatureLoop(std::vector<TemperatureSensor *> &sensorlist) : sensors(sensorlist)
	{
		FAN_MIN     = 1000;
		FAN_MAX     = 9000;
		target_temp = 50;
		Range       = 5;
		maxTemp     = 55;
		Alert       = false;
		noLED       = false;
		noALERT     = false;
	}

	int cycle(double dT = 1.0)
	{
		int cur_temp = readCurrentTemperature();
		Range = maxTemp - target_temp;
		int x = (int)cur_temp - target_temp;
		int rpm = skal((int)x, 0, Range, FAN_MIN, FAN_MAX);
		if (!noLED)
		{
			std::ofstream file("/proc/stb/fp/led_set");
			if (rpm == FAN_MIN)
			{
				file << "00";
			}
			else
			{
				file << "05";
			}
		}
		if (!noALERT)
		{
			std::ofstream file("/proc/stb/fp/led_set");
			if (rpm == FAN_MAX)
			{
				if (Alert)
				{
					file << "05";
					Alert = false;
				}
				else
				{
					file << "80";
					Alert = true;
				}
			}
			else
			{
				Alert = false;
			}
		}
		return rpm;
	}
};

int main(int argc, char *argv[])
{
	if (argc < 4)
	{
		printf("usage: %s <targettemp> <minrpm> <(no)LED> <(no)ALERT>\n", argv[0]);
		exit(1);
	}

	daemon(0, 0);

	FanParameter();

	if (!FanOK)
	{
		printf("no fan detected, exit\n");
		exit(1);
	}

	FanLoopPID fl(new FPFanControl(FanType));
	std::vector<TemperatureSensor *> sensorlist;
	for (int i = 0; i < 8; i++)
	{
		sensorlist.push_back(new FPTemperature(i));
	}
	TemperatureLoop tl(sensorlist);
	int dT = 1;

	tl.target_temp = clamp(atoi(argv[1]), 40, 50);

	if (FanType == TYPE_PWM)
	{
		tl.FAN_MIN = clamp(atoi(argv[2]), minPWM, maxRPM - 500);
	}
	else
	{
		tl.FAN_MIN = clamp(atoi(argv[2]), maxRPM / 10, maxRPM - 500);
	}

	tl.FAN_MAX = maxRPM;

	if (!strcasecmp(argv[3], "noLED"))
	{
		tl.noLED = true;
	}
	if (!strcasecmp(argv[4], "noALERT"))
	{
		tl.noALERT = true;
	}

	while (1)
	{
		fl.target_rpm = tl.cycle((double)dT);
		fl.cycle((double)dT);
		sleep(dT);
	}
}

