from django.shortcuts import render
from urllib import request
from django.http import  JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
# Create your views here.
from .models import newuser



def navbar(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


# def login(request):
#     if request.method== 'POST':
#         try:
#             Userdetailes=newuser.objects.get(Username=request.POST['Username'], pass1=request.POST['pass1'])
#             print("Username=",Userdetailes)
#             request.session['Username']=Userdetailes.Username
#             messages.success(request,"successfully login")
#             return redirect('userhome')
#         except newuser.DoesNotExist as e:   
#             messages.error(request,"Username/ Password Invalied...!")
   
#     return render(request,'login.html')


# def registration(request):
#     if request.method == 'POST':
#         Username=request.POST['Username']
#         fname=request.POST['fname']
#         lname=request.POST['lname']
#         email=request.POST['email']
#         pass1=request.POST['pass1']
#         pass2=request.POST['pass2']
#         if newuser.objects.filter(Username=Username).exists():
#             messages.warning(request,'Username is already exists')
#             return redirect('registration')
#         else:
#             newuser(Username=Username, fname=fname, lname=lname, email=email, pass1=pass1, pass2=pass2).save()
#             messages.success(request, 'The new user '+request.POST['Username']+ " IS saved successfully..!")
#             return redirect('login')
#     else:
#          return render(request,'registration.html')


def logout(request):
    # logout(request)
    messages.success(request,"successfully logout..!")
    return redirect('navbar')


# def userhome(request):
#     return render(request,'userhome.html')




def admin_login(request):
    if request.method== 'POST':
        try:
            Userdetailes=newuser.objects.get(Username=request.POST['Username'], pass1=request.POST['pass1'])
            print("Username=",Userdetailes)
            request.session['Username']=Userdetailes.Username
            messages.success(request,"successfully login")
            return redirect('userhome')
        except newuser.DoesNotExist as e:   
            messages.error(request,"Username/ Password Invalied...!")
   
    return render(request,'admin_login.html')


def admin_registration(request):
    if request.method == 'POST':
        Username=request.POST['Username']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        if newuser.objects.filter(Username=Username).exists():
            messages.warning(request,'Username is already exists')
            return redirect('admin_registration')
        else:
            newuser(Username=Username, fname=fname, lname=lname, email=email, pass1=pass1, pass2=pass2).save()
            messages.success(request, 'The new user '+request.POST['Username']+ " IS saved successfully..!")
            return redirect('admin_login')
    else:
         return render(request,'admin_registration.html')


def admin_logout(request):
    # logout(request)
    messages.success(request,"successfully logout..!")
    return redirect('navbar')

def userhome(request):
    return render(request,'userhome.html')




from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files import File
import cv2
from ultralytics import YOLO
import os
from .models import PredictedImage
from django.contrib.auth.decorators import login_required

def process_image(frame, image_path):
    # Load the YOLO model
    model = YOLO("test\\best (15).pt", "v8")
    
    # Run the model on the image
    detect_params = model.predict(source=image_path, conf=0.45, save=False)
    DP = detect_params[0].numpy()
    detected_objects = {}
    total_count = 0
    predicted_image_path = ""

    # If there are detections, process each one
    if len(DP) != 0:
        for i in range(len(detect_params[0])):
            boxes = detect_params[0].boxes
            box = boxes[i]
            clsID = box.cls.numpy()[0]
            conf = box.conf.numpy()[0]
            bb = box.xyxy.numpy()[0]
            # class_list = ["keyboard", "tv", "laptop", "mouse", "mobile", "microwave", "washing machine"]
            class_list = ["batery", "mouse", "keyword", "tv", "microwave", "mobile", "laptop" ,"printer" , "cpu", "washing machine"]
            object_name = class_list[int(clsID)]
            total_count += 1
            
            # Update the count of detected objects
            if object_name in detected_objects:
                detected_objects[object_name] += 1
            else:
                detected_objects[object_name] = 1

            # Draw the bounding box and label on the frame
            cv2.rectangle(frame, (int(bb[0]), int(bb[1])), (int(bb[2]), int(bb[3])), (255, 0, 0), 3)
            font = cv2.FONT_HERSHEY_COMPLEX
            cv2.putText(frame, f"{object_name} ({round(conf * 100, 2)}%)", (int(bb[0]), int(bb[1]) - 10), font, 1, (255, 255, 255), 2)

            # Save the predicted image
            predicted_image_path = os.path.join(settings.MEDIA_ROOT, f"{object_name}_{i}.jpg")
            cv2.imwrite(predicted_image_path, frame)

    return detected_objects, total_count, predicted_image_path



def upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Check if the uploaded file is an image
        if not uploaded_file.content_type.startswith('image'):
            return render(request, 'error.html', {'error_message': 'Uploaded file is not an image.'})
        
        # Save the uploaded image to the filesystem
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        uploaded_image_path = fs.path(filename)
        
        # Read the image using OpenCV
        frame = cv2.imread(uploaded_image_path)
        
        # Process the image and get the detection results
        detected_objects, total_count, predicted_image_path = process_image(frame, uploaded_image_path)
        
        # Save the detected image path to the database
        predicted_image = PredictedImage.objects.create(image=predicted_image_path)
        
        # Get the URL of the predicted image
        predicted_image_url = os.path.relpath(predicted_image.image.url, settings.MEDIA_ROOT)
        # Fetch user data for the logged-in user
        # logged_in_user = request.user
        # users = newuser.objects.filter(Username__icontains=logged_in_user.username)
        # Calculate total tree weights
        # Calculate total tree weights
       
        
        return render(request, 'result.html', {
            'uploaded_image': fs.url(filename),
            'detected_objects': detected_objects,
            'total_count': total_count,
            'predicted_image_url': predicted_image_url,
            #   'users': users,
            #               'total_tree_weight': total_tree_weight,

              

        })
    
    return render(request, 'upload_image.html', {'error_message': 'No file uploaded.'})



