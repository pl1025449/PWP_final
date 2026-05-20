import pickle as pk
import pi_client as cli
import time
from motor_steering import set_motor_speeds
def calibrate():
	try:
		ope=open('setting.txt','x')
		ope.close()
		#note data structure is differential, left turn, right turn
		def_data=[4,[3.8,-40,1.5],[3,40,1]]
		wr=open('setting.txt','wb')
		pk.dump(def_data,wr)
		settings=def_data
	except:
		def_data=[4,[3.8,-40,1.5],[3,40,1]]
		try:
			settings=pk.load(open('setting.txt','rb'))
		except:
			settings=def_data
	print('executing forward')
	cli.execute_command('forward')
	time.sleep(4)
	cli.execute_command('stop')
	time.sleep(2)
	print('turn right initialized')
	cli.execute_command('forward')
	time.sleep(settings[2][0])
        #print("turn right initialized")
	set_motor_speeds(settings[2][1])
	time.sleep(settings[2][2])
	cli.execute_command('forward')
	time.sleep(1)
	cli.execute_command('stop')
	time.sleep(2)
	print('turn left initialized')
	cli.execute_command('forward')
	time.sleep(settings[1][0])
        #print("turn right initialized")
	set_motor_speeds(settings[1][1])
	time.sleep(settings[1][2])
	cli.execute_command('forward')
	time.sleep(1)
	cli.execute_command('stop')
	i_n=input(f'settings are {settings}, change differential,left, right?')
	if 'end' not in i_n:
		if 'd'in i_n.lower() and not ('r'in i_n.lower() or 'l'in i_n.lower()):
			with open('setting.txt','wb') as wr:
				settings[0]=int(input('test differential:'))
				pk.dump(settings,wr)
		elif 'r'in i_n.lower() and not ('l' in i_n.lower() or 'd' in i_n.lower()):
			with open('setting.txt','wb') as wr:
				settings[2][0]=float(input('test right initial forward delay:'))
				settings[2][1]=float(input('test right turn speed'))
				settings[2][2]=float(input('test right turn length'))
				pk.dump(settings,wr)
		elif 'l'in i_n.lower() and not ('r' in i_n.lower() or 'd' in i_n.lower()):
                        with open('setting.txt','wb') as wr:
                                settings[1][0]=float(input('test right initial forward delay:'))
                                settings[1][1]=float(input('test right turn speed'))
                                settings[1][2]=float(input('test right turn length'))
                                pk.dump(settings,wr)

		calibrate()
if __name__ == "__main__":
    calibrate()
