from django.shortcuts import render,redirect
from django.views.generic import View
from django.contrib import messages
from .forms import RegisterForm, ProfileForm, PaymentForm
from .models import User, Profile
from .serializers import ProfileSerializers,ImageSerializers
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.db.models import Q
from django.views.generic.edit import UpdateView
from .models import Profile,ProfileImage,Payment
from django.views.generic.edit import FormView
from .forms import UploadForm
from django.core.mail import send_mail,BadHeaderError
from django.views.generic.detail import DetailView
from matrimonial.settings import EMAIL_HOST_USER,subject
from django.http import Http404
from operator import or_
from functools import reduce
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .decorator import user_is_entry_author
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
import shutil
import os
from django.conf import settings
import zipfile
from wsgiref.util import FileWrapper
from django.http import HttpResponse


decorators = [user_is_entry_author]


class BackUp(APIView):
    permission_classes = [IsAdminUser, ]
    def backup_call(self):
        db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
        media_path = os.path.join(settings.BASE_DIR, 'media')
        shutil.copy(db_path, media_path)
        zipf = zipfile.ZipFile('Python.zip', 'w', zipfile.ZIP_DEFLATED)
        self.zipdir(media_path, zipf)
        zipf.close()

    def zipdir(self,path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

    def get(self,request):
        self.backup_call()
        document = open(os.path.join(settings.BASE_DIR, 'Python.zip'), 'rb')
        response = HttpResponse(FileWrapper(document), content_type='application/media')
        response['Content-Disposition'] = 'attachment; filename="Python.zip"'
        return response



def login_success(request):
    if request.user.profile_active or request.user.is_superuser:
        return redirect("info:profile-list")
    else:
        return redirect("info:profile-create")

class About_Us(View):
    def get(self,request):
        return render(request,'about_us.html')


class PaymentView(LoginRequiredMixin,View):
    def get(self,request):
        try:
            payment_stat = request.user.payment
            if request.user.profile.paid:
                return redirect("info:profile-list")
        except:
            payment_stat = False
        form = PaymentForm()
        context = {'form':form ,'payment_stat':payment_stat}
        return render(request,'payment.html',context=context)

    def post(self,request):
        data = request.FILES
        print(request.POST, request.FILES)
        form = PaymentForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, "Receipt file successfully uploaded. Admin will approve and let you know")
            return redirect('info:home')
        messages.error(request, form.errors)
        return redirect('info:payment')

class Register(View):
    def get(self,request):
        form = RegisterForm()
        context = {'form':form}
        return render(request,'register.html',context=context)

    def post(self,request):
        data = request.POST
        form = RegisterForm(data)
        if form.is_valid():
            form.save()
            messages.success(request, "SuccessFully registered to Shubh Vivah Sansta! Please login and complete your profile.")
            return redirect('info:home')
        print(form.errors)
        messages.error(request, form.errors)
        return redirect('info:register')


class ProfileDetail(LoginRequiredMixin,APIView):
    serializer_class = ProfileSerializers
    queryset = Profile.objects.all()
    lookup_field = 'id'
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [IsAuthenticated]


    def get(self, request, pk=None):
        # print(serializer)
        if pk:
            if self.request.user.profile.id == pk:
                instance = get_object_or_404(Profile, id=pk)
                return Response({'profile': instance}, template_name='info/profile_update.html')
            return redirect('info:update',pk=self.request.user.profile.id)
        if request.user.profile_active:
            return redirect("info:profile-list")
        form = ProfileForm()
        return Response({'user': self.request.user},template_name='create_profile.html')


    def post(self, request,pk=None):
        if pk:
            return self.put(request,pk)
        serializer = ProfileSerializers(data=request.data)
        images = dict(request.FILES)['images']
        print(images)
        if serializer.is_valid():
            serializer.save(user=self.request.user)
            user = User.objects.get(username=request.user.username)
            for img in images:
                ProfileImage.objects.create(user=user, image=img)
            email = request.user.email
            # message = "Successfully created your profile account"
            subject = "Successfully created profile on Shubhvivahsanstha"
            message = '''Dear {},
\nThank you for submitting your details
\nFollow the instructions given below to login to Shubh Vivah Sanstha:
1. Connect to the internet and click on the link below:
https://www.shubhvivahsanstha.com 
2. login to the system using the following credentials
User Id - {}
Password - {}
\nIn case  you have any query, you can connect with us at www.shubhvivahsanstha/support.com
\nThanks,
Admin@shubhvivahvadhuvar
        '''.format(request.user.full_name,request.user.username, request.user.password)
            if request.user.email:
                try:
                    send_mail(subject, message, EMAIL_HOST_USER, [email],fail_silently=False)
                except:
                    pass
            messages.success(request, "Profile Created Successfully. Please check your email")
            return redirect('info:payment')
        messages.error(request, "Error in profile creation. Please try again")
        return redirect('info:home')

    def put(self, request, pk, format=None):
        profile = get_object_or_404(Profile,pk=pk)
        user = get_object_or_404(User,id=self.request.user.id)
        mobile_no = request.POST.get('mobile_no',None)
        email = request.POST.get('email',None)
        boolean = User.objects.filter(email=email).exists()
        if mobile_no:
            user.mobile_no = mobile_no
        if email and not boolean:
            user.email = email
        user.save()
        serializer = ProfileSerializers(profile, data=request.data)
        images = dict(request.FILES).get('images',None)
        delete_id = request.POST.get('deleteImg_id',None)
        if delete_id:
            lst = delete_id.strip().split(' ')
            for each in lst:
                ProfileImage.objects.get(id=int(each)).delete()

        if images:
            for img in images:
                ProfileImage.objects.create(user=self.request.user, image=img)

        if serializer.is_valid():
            serializer.save()
            if boolean:
                messages.success(request, "Profile Updated Successfully email not updated email already exists")
            else:
                messages.success(request, "Profile Updated Successfully")
            if request.user.profile.paid:
                return redirect('info:profile-list')
            else:
                return redirect('info:payment')
        messages.error(request, "Error in Updating")
        return redirect('info:home')


class ProfileUpdate(UpdateView):
    model = Profile
    fields = '__all__'
    template_name_suffix = '_update_form'



@method_decorator(decorators, name='dispatch')
class ProfileListView(LoginRequiredMixin,ListView):

    model = Profile
    paginate_by = 8

    def get_queryset(self):
        gender = self.request.user.gender
        queryset = Profile.objects.filter(~Q(user__gender=gender) & ~Q(user=self.request.user))
        # queryset = Profile.objects.all()
        query_dict = dict(self.request.GET)
        religion = query_dict.get("filter_religion", None)
        age = query_dict.get("filter_age",None)
        occupation = query_dict.get("filter_occupation",None)
        education = query_dict.get("filter_education",None)
        height = query_dict.get("filter_height",None)
        area = query_dict.get("filter_area",None)
        # print(religion,age,occupation,education,height,area)
        if height:
            if queryset:
                queryset = queryset.filter(Q(height__lte=height[0]))
                print("height querying")
        if religion:
            if queryset:
                queryset = queryset.filter(Q(religion__in=religion))
                print("religion querying")
        if age:
            if queryset:
                range_age = [tuple(map(int,(each.split('-')))) for each in age]
                qs = [Q(age__range=[age_min, age_max]) for (age_min, age_max) in range_age]
                age_q = reduce(or_, qs, Q())
                queryset = queryset.filter(age_q)
                print("age querying")

        if occupation:
            if queryset:
                queryset = queryset.filter(Q(occupation__in=occupation))
                print("occupation querying")
        if area:
            if queryset:
                print("area querying")
                queryset = queryset.filter(Q(district__in=area))
        if education:
            if queryset:
                print("education query")
                queryset = queryset.filter(Q(education__in=education))
        return queryset


class ProfileDetailView(DetailView):
    model = Profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = Profile.objects.get(id=self.kwargs.get('pk')).user
        user =User.objects.get(id=user.id)
        if user in self.request.user.profile.requested.all():
            context['requested'] = True
        else:
            context['requested'] = False
        return context

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        profile = get_object_or_404(Profile, id=id)
        if self.request.user.profile.id == id:
            return profile

        if profile.user.gender != self.request.user.gender:
            if self.request.user.profile.paid:
                return profile
            else:
                raise PermissionDenied
        else:
            raise Http404


class Request(LoginRequiredMixin,View):

    def get(self, request, pk=None):
        try:
            profile = get_object_or_404(Profile, (Q(id=pk) & ~Q(user__gender=self.request.user.gender) & ~Q(user__in=self.request.user.profile.requested.all())))
        except:
            raise Http404
        requested_user = profile.user
        if request.user.email:
            try:
                subject = f"Contact Information Requested by {self.request.user.full_name}"
                message = '''Greetings for the day,
                
User with Username: {} and Name: {} has shown interested in the following profile

Username: {}
Fullname: {}
    
Need to share the contact & resedential information of this profile to the requested user.
Reply to this mail with required details.

Thanks,
Admin@subhvivahvadhuvar

Replyto: {}
            '''.format(self.request.user.username,self.request.user.full_name,requested_user.username,
                           requested_user.full_name,self.request.user.email)
                send_mail(subject, message,EMAIL_HOST_USER , [EMAIL_HOST_USER],fail_silently=False)
                owner = self.request.user.profile
                owner.requested.add(requested_user)
                owner.save()
                print("mail send")
            except BadHeaderError:
                return Response({'error':'Invalid header found.'})
        messages.success(request, "Information request for this profile sent successfully. Shortly, you will receive mail from adminstrator about details of this profile")
        return redirect('info:profile-detail',pk=pk)
