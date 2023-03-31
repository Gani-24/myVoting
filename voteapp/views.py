from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import Candidate,ControlVote,Position
from django.contrib import messages
from firebase_admin import db
ref=db.reference('votes')



@login_required(login_url='login')
def HomePage(request):
    return render (request,'home.html')

def LandingPage(request):
    return render (request,'homepage.html')

def SignupPage(request):   #Getting the data from the user and saving it in the database(Django)
    if request.method=='POST':
        usname=request.POST.get('username')
        email=request.POST.get('email')
        passw=request.POST.get('password')
        usr=User.objects.create_user(usname,email,passw)
        usr.save()
        return redirect('login')
    
    return render (request,'signup.html')

def LoginPage(request): #Getting the data from the user and Checking if the user is in the database(Django)
    if request.method == 'POST':
        username=request.POST.get('ussname')
        passwd=request.POST.get('passww')
        usrr=authenticate(request,username=username,password=passwd) #authenticating the user
        if usrr is not None:
            login(request,usrr)
            return redirect('home')
        else:
            messages.warning(request,'Username or Password is Incorrect!') #Warning message on top of the webpage if username or password is incorrect
            return redirect('login')                
    return render (request,'login.html')
        

@login_required
def VotingPage(request, pos): 
    obj = get_object_or_404(Position, pk = pos)
    if request.method == "POST":

        temp = ControlVote.objects.get_or_create(user=request.user, position=obj)[0]

        if temp.status == False:
            temp2 = Candidate.objects.get(pk=request.POST.get(obj.title)) #Getting the Vote from the User
            temp2.total_vote += 1
            temp2.save()
            temp.status = True
            temp.save()
            send_vote_to_firebase(candidate_name=temp2.name, position_name=obj.title,noofvotes=temp2.total_vote) #Sending the vote to the firebase Realtime database
            return HttpResponseRedirect('/voteresult/')
        else:
            messages.success(request, 'You Have Already Voted for this Title.')
            return render(request, 'votecandi.html', {'obj':obj})
        
    else:
        return render(request, 'votecandi.html', {'obj':obj})
        
    
    
@login_required
def PositionPage(request):
    obj = Position.objects.all()
    return render(request, "position.html", {'obj':obj})

@login_required
def VoteResultPage(request):
    obj = Candidate.objects.all().order_by('position','-total_vote')
    return render(request, "voteresult.html", {'obj':obj})

def send_vote_to_firebase(candidate_name, position_name ,noofvotes):
    ref = db.reference('votes')  # Created a reference to the 'votes' node
    new_vote_ref = ref.push()  # Generating  a new unique key for the vote by the user
    new_vote_ref.set({
        'candidate_name': candidate_name,
        'position_name': position_name,
        'Live_Votes':noofvotes,
    })  # Setting the value of the new vote node to the data we want to store

def LogoutPage(request):
    logout(request)
    return redirect('login')


