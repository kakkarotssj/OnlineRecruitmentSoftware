from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views import View
from OnlineRecruitmentSoftware import connection, authhelper
from cloudant.document import Document
from cloudant.database import CloudantDatabase

"""
authcode

0: Something Else
1: Wrong Username or Password
2: Registered Sucessfull
"""

class LoginHandler(View):
	def get(self,request):
		context = {}
		if 'redirect' in request.GET:
			context["redirect"] = request.GET['redirect']
		else:
			context["redirect"] = '/profile'

		if 'authcode' in request.session:
			if request.session["authcode"] == 0:
				context['alert'] = 'danger'
				context["alertmessage"] = "Something looks Wrong"

			elif request.session["authcode"] == 1:
				context['alert'] = 'danger'
				context["alertmessage"] = "Wrong Username or Password"

			elif request.session["authcode"] == 2:
				context['alert'] = 'success'
				context["alertmessage"] = "Registration was successful! Log In to Continue"
			
			del request.session['authcode']
		else:
			context["error"] = False

		return render(request, "login/login.html", context);

	def post(self,request):

		print(request.POST)

		redirect = '/'
		if 'redirect' in request.POST:
			redirect = request.POST['redirect']
			

		if 'email' in request.POST and 'pwd' in request.POST:

			pwd = authhelper.crypt(request.POST['pwd'])
			email = request.POST['email']

			if 'org' in request.POST:
				print("log in as ORG ******* ")
				my_database = connection.conn['organization']
				print(my_database['johndoe@gmail.com'])
			else:
				print("log in as USER ******* ")
				my_database = connection.conn['users']

			if email in my_database:			
				doc = my_database[email]
				if doc['password'] == pwd:
					request.session['name'] = doc['name']
					return HttpResponseRedirect(redirect)

			request.session['authcode'] = 1
			return HttpResponseRedirect("/login?redirect="+redirect)

		request.session['authcode'] = 0
		return HttpResponseRedirect("/login?redirect="+redirect)

class LogoutHandler(View):
	def get(self,request):
		redirect = request.GET['redirect']
		del request.session['name']
		return HttpResponseRedirect(redirect)

class RegisterUser(View):
	def get(self,request):
		return render(request, "register/registeruser.html", {})

	def post(self, request):
		data = request.POST
		if 'name' in data and 'email' in data and 'pwd' in data:
			name = data['name']
			_id = data['email']
			pwd = authhelper.crypt(data['pwd'])
			my_database = connection.conn['users']
			doc = {"_id": _id, "name": name, "password": pwd}
			new_doc = my_database.create_document(doc)
			if new_doc.exists():
				request.session['authcode'] = 2
				return HttpResponseRedirect("/login?redirect=/home")
			else:
				request.session['authcode'] = 3
				return HttpResponseRedirect("/register/user")

		else:
			request.session['authcode'] = 0
			return HttpResponseRedirect("/register/user")

class RegisterOrg(View):
	def get(self,request):
		return render(request, "register/registerorg.html", {})

	def post(self, request):
		data = request.POST
		if 'name' in data and 'description' in data and 'website' in data and 'location' in data and 'category' in data and 'email' in data and 'pwd' in data :
			_id = data['email']
			name = data['name']
			desc = data['description']
			website = data['website']
			location = data['location']
			category = data['category']

			pwd = authhelper.crypt(data['pwd'])

			my_database = connection.conn['organization']

			doc = {
				"_id": _id,
				"name": name,
				"description": desc,
				"website": website,
				"location": location,
				"Category": category,
				"password": pwd,
				"verified": False
				}

			new_doc = my_database.create_document(doc)

			if new_doc.exists():
				request.session['authcode'] = 2
				return HttpResponseRedirect("/login?redirect=/home")
			else:
				request.session['authcode'] = 3
				return HttpResponseRedirect("/register/organization")

		else:
			request.session['authcode'] = 0
			return HttpResponseRedirect("/register/organization")
