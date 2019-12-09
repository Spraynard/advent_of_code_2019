def assertEquals( target, guess ):
	'''
	Assert that the guess equals the value of the target
	'''

	if guess != target:
		print('''
Unsuccessful...

Guess: {guess}
Target: {target}
'''.format( guess=guess, target=target))
		return False
	print("Test is good")
	return True