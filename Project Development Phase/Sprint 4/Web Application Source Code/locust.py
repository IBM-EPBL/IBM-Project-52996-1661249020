from msilib.schema import SelfReg
from locust import HttpUser, between, task
import time
import random

data =( {'email':'vijayit2023@gmail.com', 'password':'12345'},{'email':'tharunkumarit2023@gmail.com' , 'password':'12345'},{'email':'vijay8870605473@gmail.com', 'password':'12345'} )
post_headers={'content-type':'application/x-www-form-urlencoded'}

class WebsiteUser(HttpUser):
    wait_time=between(5,15)
    
    @task
    def index(Self):
         Self.client.get("/")

    @task
    def index(Self):
         Self.client.get("/login",
                    data=data[random.randint(0,3)],headers=post_headers)

    @task
    def index(Self):
         Self.client.get("/register",
                    data=data[random.randint(0,3)],headers=post_headers)

    @task
    def index(Self):
         Self.client.get("/verify")

    
    @task
    def index(Self):
         Self.client.get("/home")

    
    @task
    def index(Self):
         Self.client.get("/loanapplication")


    @task
    def index(Self):
        Self.client.get("/jointreport")



    
