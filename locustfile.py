import json
import random
from re import search
from locust import HttpLocust, TaskSet, task,FastHttpUser
from locust import events
#This class loads a JSON file named "performance_config_data.json" and stores it in a variable named performance_data_config

class LoadConfig:
    #Define a variable named foldersConfig and envelopesConfig
    foldersConfig = {}
    envelopesConfig = {}

    #Load the folders config by reading a json file named folders_rewrites.json and store it in the variable foldersConfig
    def load_folders_config(self):
        #Load the folders config by reading a json file named folders_rewrites.json and store it in the variable foldersConfig
        with open('config/folders_rewrites.json') as f:
            listOfFolders = json.load(f)
            #Iterate the list listOfFolders and populate the self.foldersConfig with key and value
            for item in listOfFolders:
                self.foldersConfig[item['key']] = item['value']
            
    #Load the envelopes config by reading a json file named envelopes_rewrites.json and store it in the variable envelopesConfig
    def load_envelopes_config(self):
        #Load the envelopes config by reading a json file named envelopes_rewrites.json and store it in the variable envelopesConfig
        with open('config/envelopes_rewrites.json') as f:
            listOfEnvelopesRewrite = json.load(f)                        
            #Iterate the list listOfEnvelopesRewrite and populate the self.envelopesConfig with key and value
            for item in listOfEnvelopesRewrite:
                self.envelopesConfig[item['key']] = item['value']
                    
    #Define a function named get_folders_config that returns the variable foldersConfig
    def get_folders_config(self):
        if(self.foldersConfig == {}):
            self.load_folders_config()
        return self.foldersConfig
    #Define a function named get_envelopes_config that returns the variable envelopesConfig
    def get_envelopes_config(self):
        if(self.envelopesConfig == {}):
            self.load_envelopes_config()
        return self.envelopesConfig

    #Define a function that filters Keys from get_envelopes_config for value that contains "product" 
    def get_envelopes_config_product_value(self):        
        return {v: v for k, v in self.get_envelopes_config().items() if 'product_id' in v}                
    #Define a function that filters Keys from get_folders_config for value that contains "product" 
    def get_folders_config_product_value(self):
        return {v: v for k, v in self.get_folders_config().items() if 'product_id' in v}

    #Define a function that filters Keys from get_envelopes_config for value that contains "product" 
    def get_envelopes_config_product(self):        
        return {k: v for k, v in self.get_envelopes_config().items() if 'product_id' in v}                
    #Define a function that filters Keys from get_folders_config for value that contains "product" 
    def get_folders_config_product(self):
        return {k: v for k, v in self.get_folders_config().items() if 'product_id' in v}
    
    #Define a function that filters Keys from get_envelopes_config for value that doesn't contain "product"
    def get_envelopes_config_not_product(self):
        return {k: v for k, v in self.get_envelopes_config().items() if 'product_id' not in v}
    #Define a function that filters Keys from get_folders_config for value that doesn't contain "product"
    def get_folders_config_not_product(self):
        return {k: v for k, v in self.get_folders_config().items() if 'product_id' not in v}    
    #Define an init function to initialize the class that loads the configs    
    def __init__(self):
        if(self.envelopesConfig == {}):
            self.load_envelopes_config()
        if(self.foldersConfig == {}):
            self.load_folders_config()


class LocustTasks(TaskSet):
    isEnvelopes = False
    isFolders = False
    #Define the init function that will set isFolders and isEnvelopes to True/False based on TaskSet's client's host values.
               
    #Define a variable named config that is an instance of the class LoadConfig
    load_config = LoadConfig()
    def on_start(self):
        self.load_config = LoadConfig()
        #print(f"The following is the client's host: {self.client.environment.host}")
        #See if self.client.environment.host contains "envelopes"
        if("envelopes" in self.client.environment.host):
            self.isEnvelopes = True
            self.isFolders = False
        elif("folders" in self.client.environment.host):
            self.isFolders = True
            self.isEnvelopes = False
    @task(2)
    def index(self):
        results = self.client.get("/")
        events.request.fire(request_type="GET", name="Home Page", response_code=200,response_time=4000,response_length=len(results.content) if (results.content) else 0,exception=None,context=self.user)
    
    @task(3)
    def hit_a_category(self):
        
        #get a random key from load_config's envelopesConfig        
        #Print the keys of envelopesConfig
        #print(type(self.load_config.get_envelopes_config()))
        #random_pair = random.choice(list(self.load_config.get_envelopes_config()))
        random_key = None
        if(self.isEnvelopes):
            random_key = random.choice(list(self.load_config.get_envelopes_config_not_product()))
        elif(self.isFolders):
            random_key = random.choice(list(self.load_config.get_folders_config_not_product()))
        #print("The random Pair is now: " + str(random_pair))
        
        #Get a the key from the random_pair 
        #random_key = random_pair["key"]
        #print("The random key is " + random_key)
        
        #Pass the envelope_keuy to self.user.client.get and store the response in a variable named results
        results = self.client.get(random_key)
        #results = self.user.client.get("/6-3-4-envelopes")
        events.request.fire(request_type="GET", name="Category Page", response_code=200,response_time=6000,response_length=len(results.content) if results.content else 0,exception=None,context=self.user)
    
    @task(4)
    def stop(self):
        self.interrupt()


    
    @task(4)
    def add_item_to_cart(self):
        #Get a random product number from the list of products
        product_number = None
        if(self.isEnvelopes):
            product_number = random.choice(list(self.load_config.get_envelopes_config_product_value()))
        elif(self.isFolders):
            product_number = random.choice(list(self.load_config.get_folders_config_product_value()))
        
        if(product_number):
            #Get the portion of String that has pattern of "product_id="
            #print(f"The product number is {product_number}")
            #print(f"The split product number is {product_number.split('product_id=')}")
            product_id = product_number.split("product_id=")[1]
            #print(f"The product id is {product_id}")
            results = self.client.post("/addToCart", {"quantity":1,"colorsFront":0,"colorsBack":0,"whiteInFront":0,"whiteInBack":0,"isRush":False,"cuts":0,"isFolded":False,"isFullBleed":False,"addresses":0,"add_product_id":product_id,"isProduct":True})
            events.request.fire(request_type="POST",name="AddToCart",response_time=4000,response_length=len(results.content) if results.content else 0,exception=None,context=self.user)
        else:
            results = self.client.post("/addToCart", {"quantity":1,"colorsFront":0,"colorsBack":0,"whiteInFront":0,"whiteInBack":0,"isRush":False,"cuts":0,"isFolded":False,"isFullBleed":False,"addresses":0,"add_product_id":43703,"isProduct":True})                
            events.request.fire(request_type="POST",name="AddToCart",response_time=4000,response_length=len(results.content) if results.content else 0,exception=None,context=self.user)    
        
    @task(4)
    def add_item_to_cart_and_checkout(self):
        #Get a random product number from the list of products
        product_number = None
        if(self.isEnvelopes):
            product_number = random.choice(list(self.load_config.get_envelopes_config_product_value()))
        elif(self.isFolders):
            product_number = random.choice(list(self.load_config.get_folders_config_product_value()))
        
        if(product_number):
            #Get the portion of String that has pattern of "product_id="
            #print(f"The product number is {product_number}")
            #print(f"The split product number is {product_number.split('product_id=')}")
            product_id = product_number.split("product_id=")[1]
            #print(f"The product id is {product_id}")
            results = self.client.post("/addToCart", {"quantity":1,"colorsFront":0,"colorsBack":0,"whiteInFront":0,"whiteInBack":0,"isRush":False,"cuts":0,"isFolded":False,"isFullBleed":False,"addresses":0,"add_product_id":product_id,"isProduct":True})
            results = self.client.post("/envelopes/control/placeOrder",{"oldEmailAddress": "locust-test@gmail.com","emailAddress": "locust-test@gmail.com","saved_shipping_address":"" ,"ship_to":"BUSINESS_LOCATION","shipping_firstName": "LocustFirstName","shipping_lastName": "LocustLastName","shipping_companyName": "","shipping_address1": "100 Algonquin Trl","shipping_address2": "","shipping_city": "Ashland","shipping_stateProvinceGeoId": "MA","shipping_postalCode": "01721","shipping_countryGeoId": "USA","shipping_contactNumber": "1234567890","shipping_countryCode": "","shipping_areaCode": "000","bill_to_shipping": "shipping","saved_billing_address": "","billing_firstName": "LocustFirstName","billing_lastName": "LocustLastName","billing_companyName": "","billing_address1": "100 Algonquin Trl","billing_address2": "","billing_city": "Ashland","billing_stateProvinceGeoId": "MA","billing_postalCode": "01721","billing_countryGeoId": "USA","billing_contactNumber": "1234567890","correspondingPoId": "","resellerId": "","billing_countryCode": "","billing_areaCode": "","shipping_method": "GROUND","orderNote": "","couponCode": "","cardType": "BRAINTREE_OFFLINE","paymentMethodTypeId": "PERSONAL_CHECK","checkNumber": "","externalId": ""})
            events.request.fire(request_type="POST",name="AddToCartAndCheckout",response_time=4000,response_length=len(results.content) if (results.content) else 0,exception=None,context=self.user)
        else:
            results = self.client.post("/addToCart", {"quantity":1,"colorsFront":0,"colorsBack":0,"whiteInFront":0,"whiteInBack":0,"isRush":False,"cuts":0,"isFolded":False,"isFullBleed":False,"addresses":0,"add_product_id":43703,"isProduct":True})                
            results = self.client.post("/envelopes/control/placeOrder",{"oldEmailAddress": "locust-test@gmail.com","emailAddress": "locust-test@gmail.com","saved_shipping_address":"" ,"ship_to":"BUSINESS_LOCATION","shipping_firstName": "LocustFirstName","shipping_lastName": "LocustLastName","shipping_companyName": "","shipping_address1": "100 Algonquin Trl","shipping_address2": "","shipping_city": "Ashland","shipping_stateProvinceGeoId": "MA","shipping_postalCode": "01721","shipping_countryGeoId": "USA","shipping_contactNumber": "1234567890","shipping_countryCode": "","shipping_areaCode": "000","bill_to_shipping": "shipping","saved_billing_address": "","billing_firstName": "LocustFirstName","billing_lastName": "LocustLastName","billing_companyName": "","billing_address1": "100 Algonquin Trl","billing_address2": "","billing_city": "Ashland","billing_stateProvinceGeoId": "MA","billing_postalCode": "01721","billing_countryGeoId": "USA","billing_contactNumber": "1234567890","correspondingPoId": "","resellerId": "","billing_countryCode": "","billing_areaCode": "","shipping_method": "GROUND","orderNote": "","couponCode": "","cardType": "BRAINTREE_OFFLINE","paymentMethodTypeId": "PERSONAL_CHECK","checkNumber": "","externalId": ""})            
            events.request.fire(request_type="POST",name="AddToCartAndCheckout",response_time=4000,response_length=len(results.content) if (results.content) else 0,exception=None,context=self.user)            
                

    @task(4)
    def hit_a_product(self):    
        #get a random key from load_config's envelopesConfig        
        #Print the keys of envelopesConfig
        #print(type(self.load_config.get_envelopes_config()))
        #random_pair = random.choice(list(self.load_config.get_envelopes_config()))
        random_key = None        
        if(self.isEnvelopes):
            random_key = random.choice(list(self.load_config.get_envelopes_config_product()))
        elif(self.isFolders):
            random_key = random.choice(list(self.load_config.get_folders_config_product()))
        #Pass the envelope_keuy to self.user.client.get and store the response in a variable named results
        results = self.client.get(random_key)
        #results = self.user.client.get("/6-3-4-envelopes")
        events.request.fire(request_type="GET", name="Product Page", response_code=200,response_time=6000,response_length=len(results.content) if results.content else 0,exception=None,context=self.user)

    @task(4)
    def search(self):        
        #Get a random search term from the get_envelope_product() method in load_config
        random_search_term = random.choice(list(self.load_config.get_envelopes_config_product()))        
        if(self.isFolders):
            random_search_term = random.choice(list(self.load_config.get_folders_config_product()))

        if(random_search_term):
            #Replace the / and - with spaces in random_search_term
            random_search_term = random_search_term.replace("/"," ").replace("-"," ")
            #Replace spaces with + in random_search_term
            random_search_term = random_search_term.replace(" ","+")
    
        results = self.client.get("/search?w="+random_search_term)
        events.request.fire(request_type="GET", name="Search", response_code=200,response_time=6000,response_length=len(results.content) if results.content else 0,exception=None,context=self.user)
# Create a HttpUser Class that calls the LocustTasks 
class WebsiteUser(FastHttpUser):
    #Add a header to the request with key as LoadTestUser and value as LoadTestUser!!@@2022
    headers = {'LoadTestUser': 'LoadTestUser!!@@2022'}
    tasks =  {LocustTasks:10}

    min_wait = 1000
    max_wait = 2000
    
    @task
    def my_task(self):
        pass