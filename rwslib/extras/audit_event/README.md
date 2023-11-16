# audit_event

audit_event is a simple way to consume the ODMAdapter 
[Clinical Audit Records service](https://learn.medidata.com/en-US/bundle/rave-web-services/page/odm_operational_data_model_adapter.html)

audit_event takes the approach of converting the ODM dataset provided by the clinical audit record service into a set of 
events. This is the same approach that SAX parsers take to parsing XML files.

## Capturing Events

To use the library you must first create a class that registers the events you want to capture. For instance,
if you want to count the number of subjects created you might write:

    class SubjectCounter(object):
    
        def __init__(self):
            self.count = 0
            
        def SubjectCreated(self, context):
            self.count += 1
            
        def default(self, context):
            """You can use the default event to capture all events that you have not defined a handler for
               the default handler is also optional, you do not have to define it.
            """
            pass
    
Events raised are named after the audit subcategory for each reported audit in the ODM stream. See a 
[full list of event names](https://learn.medidata.com/en-US/bundle/rave-web-services/page/included_audit_subcategories_in_rws.html)

*NOTE*
* From Rave EDC 2022.3.0 onwards: 
  * the ODM Adapter Version 2 provides Clinical Audit Record (CAR) extracts for all the Audit Subcategories (ASCs) available for Rave EDC clinical data. 
  * the ODM Adapter V2 Clinical Audit Records (CAR) service has introduced an optional query string parameter, `mode`, to allow you to extract additional ASCs. 

The _context_ object passed contains all the data pulled from the audit record. 

    Context:
        study_oid
        subcategory
        metadata_version
        subject
            key
            name
            status
            transaction_type          
        event
            oid
            repeat_key
            transaction_type
            instance_name
            instance_overdue
            instance_id
        form
            oid
            repeat_key
            transaction_type
            datapage_name
            datapage_id
        itemgroup
            oid
            repeat_key
            transaction_type
            record_id  
        item
            oid 
            value
            freeze
            verify
            lock
            transaction_type     
        audit_record
            user_oid
            location_oid
            datetimestamp
            reason_for_change
            source_id
        query
            repeat_key
            status
            response
            recipient
            value
        protocol_deviation
            repeat_key 
            code
            klass
            status 
            value
            transaction_type      
        comment
            repeat_key 
            value 
            transaction_type         
        review
            group_name
            reviewed
        signature
            oid 
            user_oid 
            location_oid 
            datetimestamp                 
        
What you look for in the context object depends on the audit subcategory type. For instance in the case of
the SubjectCreated event there will be no value for event, item, review, signature etc. In the case of a signature
event of some kind the signature attribute will be populated with a context.Signature object.

The purpose of this scheme is to cope with the many different types of audit events that can be reported via the
clinical audits dataset.

## Using ODMAdapter

ODMAdapter is a class that takes a RWSConnection, the name of the study and environment you want to process for 
events and an instance of your eventer class.

the run() method starts ODMAdapter using the RWSConnection credentials to pull audits from the study, passing them to
your event capturing class for reporting.


    # Define a counting class
    class SubjectCounter(object):
    
        def __init__(self):
            self.count = 0
            
        def SubjectCreated(self, context):
            self.count += 1
            
    # Create one
    counter = SubjectCounter()
    
    # Make a connection
    c = RWSConnection("ravedemo7","myusername","**mypassword**")
    
    # Pass connection and counter to the ODMAdapter along with the study name/environment we want to process
    o = ODMAdapter(c, "MEDICILLIN-RD7","DEMO", counter )
    
    # Run the adapter
    o.run()
    
    # get the count
    print counter.count
    
The ODMAdapter run() method takes a number of optional arguments. By default it will start with audit id 0 and keep
requesting pages of data (with audit 1000 records per page, the minimum) until the Clinical Audit Records webservice 
says that there is no more data. 

The options to run() are:

    start_id=0      # Which audit id to start ar (great for daily/hourly incremental pulls from the service)
    max_pages=-1    # How many pages of data to pull (-1 means all pages)
    per_page=1000   # The size (in audit records) of each request - 1,000 is min, higher takes more memory/time
    mode            # Allow extraction of additional ASCs
    
## Working out which id to start on
    
If we planned to run our Subject Counter on a regular basis, we wouldn't want to start from the beginning of the 
"audit tape" each time, that would be inefficient. Instead, we could change our SubjectCounter class to track the
last id it saw and ask for this value +1 the next time.

    class SubjectCounter(object):
    
        def __init__(self):
            self.count = 0
            self.max_id = 0
            
        def SubjectCreated(self, context):
            self.count += 1
            self.max_id = context.audit_record.source_id
            
        def default(self, context):
            self.max_id = context.audit_record.source_id
           
Now at the end of a run we can ask for the max_id and feed that back into the ODMAdapter .run(start_id=max_id+1) 
method.