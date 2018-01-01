
from __future__ import unicode_literals
import json
from django.shortcuts import render
from django.http import HttpResponse
from FormApi.models import Users,Context_for_year
from FormApi import Constant 
from django.views.decorators.csrf import csrf_exempt
from FormApi.form import SendEmailForm,UsersForm,UploadFileForm
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import openpyxl
from io import BytesIO

# Create your views here.
@csrf_exempt
def Login(request):
	if request.method == "POST":
		username = request.POST[Constant.Username]
		password = request.POST[Constant.Password]
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect("/Sendmail")
		message = "Login falied,error login"
		return render(request,"login.html",{'message':message})
	elif request.user.is_authenticated:
		return redirect(Sendmail)
	else:
		return render(request,"login.html")
		
	# try:
	# 	username = str(data[Constant.Username])
	# except:
	# 	return HttpResponse("username not provided")

	# try:
	# 	email = str(data[Constant.Email])
	# except:
	# 	return HttpResponse("email not provided")
	
	# try:
	# 	phone = str(data[Constant.Phone])
	# except:
	# 	phone = str(Constant.empty)

	# try:
	# 	year = int(data[Constant.Year])
	# except:
	# 	year = 2015
	# try:
	# 	rollno = str(data[Constant.Rollno])
			
	# except:
	# 	rollno = ""	
	# newuser = Users.objects.create(UserName = username,Email=email,Phone=phone,Rollno=rollno,Year=year)
	# newuser.save()

	# json_form = json.dumps({Constant.Username:newuser.UserName,
	# 			Constant.Year:newuser.Year,
	# 			Constant.Rollno:newuser.Rollno,
	# 			Constant.Email:newuser.Email,
	# 			Constant.Phone:newuser.Phone})
	# print(json_form)

	# return HttpResponse(json_form,content_type=Constant.content_type)

def Logout(request):
	logout(request)
	return redirect(Login)




@login_required
def FillData(request):
	if request.method == "POST":
		UsersForms = UsersForm(request.POST)
		if UsersForms.is_valid():
			username = UsersForms.cleaned_data[Constant.Username]
			phone = UsersForms.cleaned_data[Constant.Phone]
			email = UsersForms.cleaned_data[Constant.Email]
			year = UsersForms.cleaned_data[Constant.Year]
			rollno = UsersForms.cleaned_data[Constant.Rollno]
			

			newuser = Users.objects.create(UserName = username,Email=email,Phone=phone,Rollno=rollno,Year=year)
			newuser.save()
			messages = "Successfully added Student Detail"
			UsersForms = UsersForm()
			return render(request,'filldata.html',{'UsersForms':UsersForms,"messages":messages})



		message = "error during validation of form"
		return render(request,'filldata.html',{'UsersForms':UsersForms,"message":message})

	else:
		UsersForms = UsersForm()
		return render(request,'filldata.html',{'UsersForms':UsersForms})

	# data = json.loads(request.body)	
	# try:
	# 	username = str(data[Constant.Username])
	# except:
	# 	return HttpResponse("username not provided")

	# try:
	# 	email = str(data[Constant.Email])
	# except:
	# 	return HttpResponse("email not provided")
	
	# try:
	# 	phone = str(data[Constant.Phone])
	# except:
	# 	phone = str(Constant.empty)

	# try:
	# 	year = int(data[Constant.Year])
	# except:
	# 	year = 2015
	# try:
	# 	rollno = str(data[Constant.Rollno])
			
	# except:
	# 	rollno = ""	
	# newuser = Users.objects.create(UserName = username,Email=email,Phone=phone,Rollno=rollno,Year=year)
	# newuser.save()

	# json_form = json.dumps({Constant.Username:newuser.UserName,
	# 			Constant.Year:newuser.Year,
	# 			Constant.Rollno:newuser.Rollno,
	# 			Constant.Email:newuser.Email,
	# 			Constant.Phone:newuser.Phone})
	# print(json_form)

	# return HttpResponse(json_form,content_type=Constant.content_type)


@login_required
def Sendmail(request):
	log = 0
	if request.method == 'POST':
		SendEmailform = SendEmailForm(request.POST)
		if SendEmailform.is_valid():
			subject = SendEmailform.cleaned_data[Constant.Subject]
			body = SendEmailform.cleaned_data[Constant.Body]
			value1 = SendEmailform.cleaned_data[Constant.Sorting]
			for year in value1:
				values = Users.objects.filter(Year=int(year))
				Email(values,subject,body)

			messages = "Email send succesfully"
			return render(request,'form.html',{'SendEmailform':SendEmailform,"messages":messages})
		
		message = "Error during validation of form, please fill correct email data"
		return render(request,'form.html',{'SendEmailform':SendEmailform,"message":message})
	else:
		SendEmailform = SendEmailForm()
		return render(request,'form.html',{'SendEmailform':SendEmailform})


@login_required
def FillDataExcel(request):
	if request.method == 'POST':
		form = UploadFileForm(request.POST, request.FILES)
		file = request.FILES['file'].read()
		wb= openpyxl.load_workbook(filename=BytesIO(file))
		arraylist = []
		sheet=wb.get_sheet_by_name('Sheet1')
		for row in sheet.iter_rows():
			arraylist_inside = []
			for data in row:
				arraylist_inside.append(data.value)
			arraylist.append(arraylist_inside)

		message = Excel(arraylist)

		if message ==1:
			messages = "Succesfully created student details"
			return render(request,'uploadfile.html',{'messages':messages,'form':form})
		else:
			return render(request,'uploadfile.html',{'message':message,'form':form})	
	else:
		form = UploadFileForm()
		return render(request,'uploadfile.html',{'form':form})
	


def Email(userlist,subject,body):
	for user in userlist:
		email1 = user.Email
		email = EmailMessage(subject,body,to=[email1])
		value = email.send()


def Excel(array):
	try:
		username_index = array[0].index(Constant.Username)
	except:
		message = "Provide UserName heading properly in the Excel data"
		return message

	try:
		email_index = array[0].index(Constant.Email)
	except:
		message = "Provide Email heading properly in the Excel data"
		return message

	try:
		phone_index = array[0].index(Constant.Phone)
	except:
		message = "Provide Phone heading properly in the Excel data"
		return message

	try:
		rollno_index = array[0].index(Constant.Rollno)
	except:
		message = "Provide Rollno heading properly in the Excel data"
		return message
	try:
		year_index = array[0].index(Constant.Year)
	except:
		message = "Provide Year heading properly in the Excel data"
		return message
	
	errorlist = []
	for row in array[1:]:
		username = row[username_index]
		email = row[email_index]
		year = row[year_index]
		phone = row[phone_index]
		rollno = row[rollno_index]
		try:
			try:
				newuser = Users.objects.get(UserName = username,Email=email)
			except:
				newuser = Users.objects.create(UserName = username,Email=email,Phone=phone,Rollno=rollno,Year=year)
				newuser.save()
		except:
			errorlist.append(username)


	if errorlist:
		message = "Error creating student details for username " +errorlist[0]
		return message
	else:
		return 1




