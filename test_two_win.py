'''
  If you ever wondered how overlaying works in python curses lib so did I! This is how it works:
'''

import curses

def start(stdscr):
	# sets up no delay so keys dont overload CPU
	stdscr.nodelay(False)
	# no blinking cursor
	curses.curs_set(False)
	# bare nececity
	stdscr.refresh()

	win1 = curses.newwin(6,6)
	win1.border()
	[win1.addstr(line+1,1,"a"*4) for line in range(4)]
	win1.refresh()
	'''
	Initial window we have:
	┌────┐
	│aaaa│
	│aaaa│
	│aaaa│
	│aaaa│
	└────┘
	'''
	stdscr.getch()

	win2 = curses.newwin(6,6,2,2)
	win2.border()
	win2.refresh()
	'''
	Nope!
	┌────┐
	│aaaa│
	│a┌────┐
	│a│    │
	│a│    │
	└─│    │
	  │    │
	  └────┘
	Note: adding win1.refresh() wont do it either
	 '''
	stdscr.getch()

	[win2.addstr(line+1,1," "*4) for line in range(4)]
	win2.overlay(win1) # introducing
	win2.refresh()
	win1.refresh()
	'''
	So you need to add win2.overlay(win1) and 
	refresh BOTH windows in order for this to work
	┌────┐
	│aaaa│
	│a┌────┐
	│a│aa│ │
	│a│aa│ │
	└─│──┘ │
	  │    │
	  └────┘
	'''
	stdscr.getch()

	[win2.addstr(line+1,1," b"*2) for line in range(4)]
	win2.refresh()
	win1.refresh()
	'''
	Dont think you are finished yet!
	┌────┐
	│aaaa│
	│a┌────┐
	│a│ b b│
	│a│ b b│
	└─│ b b│
	  │ b b│
	  └────┘
	'''

	stdscr.getch()

	[win2.addstr(line+1,1," b"*2) for line in range(4)]
	win2.overlay(win1)
	win2.refresh()
	win1.refresh()
	'''
	You need to call overlay method every time
	you need to change win2
	┌────┐
	│aaaa│
	│a┌────┐
	│a│ab│b│
	│a│ab│b│
	└─│─b┘b│
	  │ b b│
	  └────┘
	'''

	stdscr.getch()

	win2.clear() # lets get rid of that border and see how things go
	[win2.addstr(line+1,1," b"*2) for line in range(4)] # adding same b pattern
	win2.overlay(win1)
	win2.refresh()
	win1.refresh()
	'''
	somethings off here:
	┌────┐
	│aaaa│
	│a
	│a  b b
	│a  b b
	└─  b b
	    b b

	'''
	stdscr.getch()

	win2.addstr(0,0, ".") # turns out you need character that is not " " at 0,0 position but!
	win2.overlay(win1)
	win2.refresh()
	win1.refresh()
	'''
	even tho we have cleared the border it somehow stayed 
	there when we have rendered it, a bug maybe
	┌────┐
	│aaaa│
	│a ───
	│a│ab│b
	│a│ab│b
	└─│─b┘b
	    b b

	'''

	stdscr.getch()

	win2.clear() # lets get rid of that border and see how things go
	[win2.addstr(line+1,1," b"*2) for line in range(4)] # adding same b pattern
	win2.addstr(0,0, ".") 
	win2.overlay(win1)
	win2.refresh()
	win1.refresh()
	'''
	somethings off here as well, not sure why but borders are demon like,
	lets try and skip borders for now, and if you dont want to go borders
	on the overlay window dont from the start, dont try to clear:
	┌────┐
	│aaaa│
	│a.
	│a  b b
	│a  b b
	└─  b b
	    b b

	'''
	stdscr.getch()

	win1.clear()
	win2.clear() # lets get rid of that border and see how things go
	[win2.addstr(line+1,1," b"*2) for line in range(4)] # adding same b pattern
	win1.border()
	[win1.addstr(line+1,1,"a"*4) for line in range(4)]
	win2.overlay(win1)
	win1.refresh()
	'''
	turns out we need to clear win1 as well when we clear win2,
	borders are demonlike, no extra char at 0,0 this time:
	┌────┐
	│aaaa│
	│aaaa│
	│aaab│b
	│aaab│b
	└───b┘b
	    b b


	'''
	stdscr.getch()

	win2.overlay(win1)
	win2.refresh()
	win1.refresh()
	'''
	but, try and refresh it and its broken again:
	┌────┐
	│aaaa│
	│a
	│a  b b
	│a  b b
	└─  b b
	    b b

	'''

	stdscr.getch()

	del win1
	del win2

	win1 = curses.newwin(6,6)
	win2 = curses.newwin(6,6,2,2)
	win1.border()
	[win1.addstr(line+1,1,"a"*4) for line in range(4)]
	[win2.addstr(line+1,1," b"*2) for line in range(4)] # adding same b pattern
	win2.overlay(win1)
	win2.refresh()
	win1.refresh()

	win2.overlay(win1)
	win2.refresh()
	win1.refresh()
	'''
	ok, another try, this time we delete instaed of clear and
	refresh it two times:
	┌────┐
	│aaaa│
	│aaaa│
	│aaab│b
	│aaab│b
	└───b┘b
	    b b

	'''

	stdscr.getch()

	[win1.addstr(line+1,1,"b"*4) for line in range(4)]
	[win2.addstr(line+1,1," c"*2) for line in range(4)] # adding same b pattern
	win2.overlay(win1)
	win2.refresh()
	win1.refresh()

	'''
	making sure everything works!
	┌────┐
	│bbbb│
	│bbbb│
	│bbbc│c
	│bbbc│c
	└───c┘c
	    c c
	'''

	stdscr.getch()

curses.wrapper(start)