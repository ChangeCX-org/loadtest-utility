# loadtest-utility
Load testing script using locust.io.
## Introduction
This repository would hold script (locustfile.py) which contains Tasks to execute performance script for multiple webistes. We are using Rewrite file of a typical ecommerce website to generate dynamic randomized load. Users using this script will be able to test 
<ol>
  <li>
    Home page
  </li> 
  <li>
    category Pages (Randomness is ensured by looking at a random URL for each worker/Task from rewrites of the site)
  </li>
  <li> 
    Product Page (Randomness is ensured by looking at a random URL for each worker/Task from rewrites of the site)    
  <li>
    Shopping Cart   (Randomness is ensured by looking at a random Product to add to bag for each worker/Task from rewrites of the site)
  </li>
  <li>
    Checkout as anonymous user   (Randomness is ensured by looking at a random Product to add to bag for each worker/Task from rewrites of the site)
  </li>
</ol>
## Configuration

Please look at config/envelopes_rewrite.json and config/folders_rewrite.json

## Structure of locustfile.py

### LoadConfig Class
This class is the key class that loads the two configuration JSONs mentioned above. Loading this during start of load test ensures that each worker of the load test is able to get Random URL

### LocustTasks(TaskSet) Class 
This class is the workhorse which contains collection of tasks with a task weight. Each task is an action that would be executed by the load test worker. In our case we have Home page task, hit_a_product task (For Product details page), hit_a_category Task (For hitting Category Page), add_item_to_cart Task for hitting add item to bag and finally add_item_to_cart_and_checkout task for adding item to cart and doing a checkout using Paper Check. 

### WebsiteUser Class (Extends FastHttpUser)
This class is a sub class of FastHttpUser which accelarates the load of workers to expedite the tests. This class creates a tasks variable which contains LocustTasks as its input and triggers the load test. 

## To Invoke the load test script locally use this steps
### Install locust on local 
<code> pip install locust</code> <br>
<code>locust -f locustfile.py --host https://qa.testenvelopes.com </code>
