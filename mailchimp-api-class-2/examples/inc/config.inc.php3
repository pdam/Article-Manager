<?php

##    [access_token] => 6c2325c7203ff729aacbdacb03b326c1
##    [expires_in] => 0
##    [scope] => 
##    [base_domain] => 
##    [expires] => 1342427389
##    [refresh_token] => 
##    [secret] => 74a20cd4bee7f873762ef746b80563c5
##    [sig] => 20254229620d5ff649030bc070231ef6
##)
##
##And here are the results of the follow-up metadata call:
##
##Array
##(
##    [dc] => us5
##    [login_url] => https://login.mailchimp.com
##    [api_endpoint] => https://us5.api.mailchimp.com



    //API Key - see http://admin.mailchimp.com/account/api
    $apikey = '10714a6eca58e14a77865dcf51a36b36';
    
    // A List Id to run examples against. use lists() to view all
    // Also, login to MC account, go to List, then List Tools, and look for the List ID entry
    $listId = 'YOUR MAILCHIMP LIST ID - see lists() method';
    
    // A Campaign Id to run examples against. use campaigns() to view all
    $campaignId = 'YOUR MAILCHIMP CAMPAIGN ID - see campaigns() method';

    //some email addresses used in the examples:
    $my_email = 'pdam.2010@gmail.com';
    $boss_man_email = 'kabir.seth@gmail.com';

    //just used in xml-rpc examples
    $apiUrl = 'http://api.mailchimp.com/1.3/';
    
?>
