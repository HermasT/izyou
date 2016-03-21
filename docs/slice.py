# qr
@app.route('/qr')
def qr():
	img = qrcode.make('sign info')
	img.save('portal/static/tmp/test.png','PNG')
	return render_template('qr.html')

# 关于
@app.route('/about', methods=['GET'])
def about():
	try:
		username = current_user.username
		return render_template('about.html', index=2, user=username)
	except:
		return render_template('about.html', index=2, user=None)

# 师资
@app.route('/faculty', methods=['GET', 'POST'])
def faculty():
	try:
		username = current_user.username
		return render_template('faculty.html', index=3, user=username)
	except:
		return render_template('faculty.html', index=3, user=None)