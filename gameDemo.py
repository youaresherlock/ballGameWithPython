# -*- coding: utf-8 -*-
# @Author: Clarence
# @Date:   2018-03-11 09:18:23
# @Last Modified by:   Clarence
# @Last Modified time: 2018-03-13 19:53:46
"""
将玻璃板放到屏幕的下方正中央
如何改变鼠标光标图片?
改变鼠标光标,自定义鼠标的光标
mouse模块中可以将光标设置为不可见，实时获取鼠标光标位置，
设置鼠标光标是否可见: pygame.mouse.set_visible()
	set_visible(bool) -> bool
	If the bool argument is true, the mouse cursor
	will be visible. This will return the previous 
	visible state of the cursor.
获取鼠标光标位置: pygame.mouse.get_pos()
	get_pos() -> (x, y)
	Return the X and Y position of the mouse cursor.

用图片代替就行了
在玻璃板上鼠标移动频率决定了匹配哪个小球
1.为每个小球设定一个不同的目标;
2.创建一个motion变量来记录鼠标每1秒钟产生事件数量。
3.为小球添加一个check()方法，用于判断鼠标在1秒钟时间内
产生的事件数量匹配是否此目标;
4.添加一个自定义事件，每1秒钟触发1次。调用每个小球的check()检测是
motion的值是否匹配某一个小球的目标，并将motion重新初始化，以便记录下1
秒的鼠标事件数量.
5.小球应该添加一个control属性，用于记录当前的状态(绿色->玩家控制
灰色->随机移动)
6.通过检查control属性来决定绘制什么颜色的小球
如何重复在事件队列中创建事件?
pygame.time.set_timer(eventid, milliseconds) -> None
	Set an event type to appear on the event queue every 
	given number of milliseconds. The first event will
	not appear until the amount of tiem has passed.

玩家通过键盘上的WASD按键可以控制小球的移动方向

为了使玩家控制的小球有加速度的快感，所以设置同一个按键事件可以
重复多次
pygame.key.set_repeat(delay, interval) -> None
	When the keyboard repeat is enabled, keys that are held 
	down will generate multiple pygame.KEYDOWN events. The 
	delay is the number of milliseconds before the first 
	repeated pygame.KEYDOWN will be sent.After that another 
	pygame.KEYDOWN will be sent every interval milliseconds.
	IF no arguments are passed the key repeat is disabled.
	When pygame is initialized the key repeat is disabled.'
--delay参数指定第一次发送事件的延迟时间
--interval参数指定重复发送事件的时间
--如果不带任何参数，表示取消重复发送事件

游戏规则:在玻璃面板上滑动鼠标，会选择对应的小球变为绿色，停止后由玩家
wasd键控制方向移动，将一个小球填入黑洞中时按下空格键则锁定小球，将
所有小球都填入黑洞中则游戏胜利(每个黑洞只能填入一个绿色的小球;当小球填入
黑洞的时候，其他小球只能从最上面飘过)

"""
import  pygame
import traceback
import sys
from pygame.locals import *
from random import *

class Ball(pygame.sprite.Sprite):
	def __init__(self, grayball_image,greenball_image, position, speed, bg_size, target):
		# Call the parent class (Sprite) constructor
		pygame.sprite.Sprite.__init__(self)

		self.grayball_image = pygame.image.load(grayball_image).convert_alpha()
		self.greenball_image = pygame.image.load(greenball_image).convert_alpha()
		self.rect = self.grayball_image.get_rect()
		#小球的位置
		self.rect.left, self.rect.top = position
		#速度的方向
		self.side = [choice([-1, 1]), choice([-1, 1])]
		self.speed = speed
		#小球是否发生碰撞
		self.collide = False
		#频率达到target左右一定范围内小球停下来
		self.target = target
		#没有被玩家控制状态
		self.control = False

		self.width, self.height = bg_size[0], bg_size[1]
		#self.width = self.width / 2

	'''
	Pygame.Rect.move():
		moves the rectangle 
		move(x, y) -> Rect
		Returns a new rectangle that is moved by the given offset. The
		x and y arguments can be any integer value, positive or 
		negative.
		可以在Rect对象的move方法中添加可正可负的两元素
		如果要实现小球的移动，则要在类中添加一个move()方法，并且在绘图的时候调用小球
		对象的move()方法
	'''
	def move(self):
		if self.control:
			#玩家控制的小球移动有方向(事件中大小和方向是用一个变量speed表示)
			self.rect = self.rect.move(self.speed)
		else:
			self.rect = self.rect.move((self.side[0] * self.speed[0],\
			self.side[1] * self.speed[1]))

		#类似实现贪吃蛇穿入墙壁从对面墙壁出来(左右方向)
		if self.rect.right <= 0:
			self.rect.left = self.width
		elif self.rect.left >= self.width:
			self.rect.right = 0

		#(上下方向) 从下往上 和 从上往下
		elif self.rect.bottom <= 0:
			self.rect.top = self.height
		elif self.rect.top >= self.height:
			self.rect.bottom = 0

	#check()方法，判断鼠标在1秒钟内产生的事件数是否匹配此目标
	def check(self, motion):
		if self.target < motion < self.target + 5:
			return True
		else:
			return False

#玻璃面板类
class Glass(pygame.sprite.Sprite):
	def __init__(self, glass_image, mouse_image, bg_size):
		#初始化动画精灵
		pygame.sprite.Sprite.__init__(self)
		
		self.glass_image = pygame.image.load(glass_image).convert_alpha()
		self.glass_rect = self.glass_image.get_rect()
		self.glass_rect.left, self.glass_rect.top = \
		(bg_size[0] - self.glass_rect.width) // 2,\
		(bg_size[1] - self.glass_rect.height) 

		self.mouse_image = pygame.image.load(mouse_image).convert_alpha()
		self.mouse_rect = self.mouse_image.get_rect()
		#图标初始位置在玻璃板的左上角
		self.mouse_rect.left, self.mouse_rect.top = \
		self.glass_rect.left, self.glass_rect.top

		#设置鼠标光标不可见
		pygame.mouse.set_visible(False)


def main():
	pygame.init()

	grayball_image = "gray_ball.png"
	greenball_image = "green_ball.png"
	glass_image = "glass.png"
	bg_image = "background.png"
	mouse_image ="hand.png"

	running = True

	# 添加模型的背景音乐
	pygame.mixer.music.load("bg_music.ogg")
	pygame.mixer.music.play()

	# 添加音效
	loser_sound = pygame.mixer.Sound("loser.wav")
	laugh_sound = pygame.mixer.Sound("laugh.wav")
	winner_sound = pygame.mixer.Sound("winner.wav")
	hole_sound = pygame.mixer.Sound("hole.wav")

	# 音乐播放完时游戏结束,将GAMEOVER事件加入到事件队列中去
	# USEREVENT为用户自定义的事件
	# 如果想定义第二个事件可以是GAMEOVERTWO = USEREVENT + 1
	GAMEOVER = USEREVENT
	#背景音乐结束后发生GAMEOVER事件消息
	pygame.mixer.music.set_endevent(GAMEOVER)

	# 根据背景图片指定游戏界面尺寸
	bg_size = width, height = 1024, 681
	screen = pygame.display.set_mode(bg_size)
	pygame.display.set_caption("Play the Ball")

	#.png格式可以加入apha通道
	background = pygame.image.load(bg_image).convert_alpha()

	#黑洞的位置 留有一定的冗余(每个黑洞的范围(x1, x2, y1, yw))
	hole = [(117, 119, 199, 201), (225, 227, 390, 392), \
	(503, 505, 320, 322), (698, 700, 192, 194),\
	(906, 908, 419, 421)]

	msgs = []

	#用来存放小球对象的列表
	balls = []
	# group A container class to hold and mangage multiple Sprite objects
	group = pygame.sprite.Group()

	for i in range(5):
		#球的尺寸是100*100 随机产生小球的位置
		position = randint(0, width-100), randint(0, height-100)
		#两个元素的一个列表，表示x轴和y轴方向的速度
		speed = [randint(1, 10), randint(1, 10)]
		#实例化小球对象 分别传入Surface对象 位置二元组 速度两元素列表
		ball = Ball(grayball_image, greenball_image, position, speed, bg_size, 5 * (i + 1))
		#碰撞检测之后不从组里面删除
		while pygame.sprite.spritecollide(ball, group, False, pygame.sprite.collide_circle):
			ball.rect.left, ball.rect.top = randint(0, width - 100),\
			randint(0, height - 100)

		balls.append(ball) #将小球加入到小球列表中
		group.add(ball)

	glass = Glass(glass_image, mouse_image, bg_size)

	#创建motion变量记录鼠标1秒钟产生事件数量
	motion = 0

	# 添加自定义事件，每1秒触发一次.调用每个小球
	# check()检测motion的值是否匹配某一个小球的
	# target，并且初始化motion
	MYTIMER = USEREVENT + 1
	pygame.time.set_timer(MYTIMER, 1000)

	pygame.key.set_repeat(100, 100)

	# CLock()对象用来设置小球的帧率
	clock = pygame.time.Clock()

	while  running:
		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit()

			elif event.type == GAMEOVER:
				loser_sound.play()
				pygame.time.delay(2000)
				laugh_sound.play()
				running = False #结束循环

			elif event.type == MYTIMER:
				if motion:
					for each in group:
						if each.check(motion):
							each.speed = [0, 0]
							each.control = True
					motion = 0

			elif event.type == MOUSEMOTION:
				motion += 1

			elif event.type == KEYDOWN:
				if event.key == K_w:
					for each in group:
						if each.control:
							each.speed[1] -= 1

				if event.key == K_s:
					for each in group:
						if each.control:
							each.speed[1] += 1

				if event.key == K_a:
					for each in group:
						if each.control:
							each.speed[0] -= 1

				if event.key == K_d:
					for each in group:
						if each.control:
							each.speed[0] += 1

				if event.key == K_SPACE:
					for each in group:
						if each.control:
							for i in hole:
								if i[0] <= each.rect.left <= i[1] and\
								i[2] <= each.rect.top <=i[3]:
									hole_sound.play()
									each.speed = [0, 0]
									# 固定的小球不在组里面，不会进行碰撞检测
									group.remove(each)
									temp = balls.pop(balls.index(each))
									# 先绘制固定在黑洞中的小球，然后在绘制其他的
									balls.insert(0, temp)
									# 将列表中对应被绿色小球占领的黑洞给去掉
									hole.remove(i)

							#游戏胜利，所有的黑洞都被绿色小球填满
							if not hole:
								pygame.mixer.music.stop()
								winner_sound.play()
								#延迟一段时间播放胜利音乐
								pygame.time.delay(3000)
								# msg是一个Surface对象，有一个方法get_width()获取Surface对象的宽度像素值
								msg = pygame.image.load("win.png").convert_alpha()
								msg_pos = (width - msg.get_width()) // 2,\
								(height - msg.get_height()) // 2
								msgs.append((msg, msg_pos))
								laugh_sound.play()

		screen.blit(background, (0, 0))
		#注意绘制先后顺序，要不然小球会从玻璃面板下面穿过
		screen.blit(glass.glass_image, glass.glass_rect)

		# 绘制当前帧鼠标的光标位置
		glass.mouse_rect.left, glass.mouse_rect.top = pygame.mouse.get_pos()
		#限制鼠标只能在玻璃面板内移动

		#鼠标光标位置小于玻璃面板左侧位置
		if glass.mouse_rect.left < glass.glass_rect.left:
			glass.mouse_rect.left = glass.glass_rect.left

		if glass.mouse_rect.left > glass.glass_rect.right - glass.mouse_rect.width:
			glass.mouse_rect.left = glass.glass_rect.right - glass.mouse_rect.width

		if glass.mouse_rect.top < glass.glass_rect.top:
			glass.mouse_rect.top = glass.glass_rect.top

		if glass.mouse_rect.top > glass.mouse_rect.bottom - glass.mouse_rect.height:
			glass.mouse_rect.top = glass.mouse_rect.bottom - glass.mouse_rect.height

		screen.blit(glass.mouse_image, glass.mouse_rect)



		for each in balls:
			each.move()
			if each.collide:
				#改变速度的大小
				each.speed = [randint(1, 10), randint(1, 10)]
				each.collide = False
			if each.control:
				# 玩家控制，画绿色小球
				screen.blit(each.greenball_image, each.rect)
			else:
				screen.blit(each.grayball_image, each.rect) 

		for each in group:
			group.remove(each)

			if pygame.sprite.spritecollide(each, group, False, pygame.sprite.collide_circle):
				'''
				为了增加游戏的难度，使小球碰撞后获得随机的一个速度，但是这会造成小球可能在一起震荡
				震荡原因:两个小球发生碰撞之后可能产生的随机速度是相向的，因此会再次碰撞;如果是产生的
				随机速度是相反的，速度不够大脱离彼此也不行，否则会再次碰撞 因此先将速度的方向和大小分离开来，
				最后再整合起来
				each.speed = [randint(-10, 10), randint(-10, 10)]
				'''
				each.side[0] = -each.side[0]
				each.side[1] = -each.side[1]

				each.collide = True
				#由于玩家控制的小球speed同时表示大小和方向，因此碰撞后要调整成反向
				if each.control:
					each.side[0] = -1
					each.side[1] = -1
					#使玩家控制的小球碰撞之后不再被控制
					each.control = False

			group.add(each)

		for msg in msgs:
			screen.blit(msg[0], msg[1])

		pygame.display.flip() #将显示缓冲区中的数据刷入显示器中
		clock.tick(30)

if __name__ == "__main__":
	#执行.exe文件的时候捕获异常
	try:
		main()
	except SystemExit:
		traceback.print_exc()
		pygame.quit()
		input()
