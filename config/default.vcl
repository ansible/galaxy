backend default {
  .host = "127.0.0.1";
  .port = "8080";
}

sub vcl_recv {
    # unless sessionid/csrftoken is in the request, don't pass ANY cookies (referral_source, utm, etc)
    if (req.request == "GET" && (req.url ~ "^/static" || (req.http.cookie !~ "sessionid" && req.http.cookie !~ "csrftoken"))) {
        remove req.http.Cookie;
    }
 
    # normalize accept-encoding to account for different browsers
    # see: https://www.varnish-cache.org/trac/wiki/VCLExampleNormalizeAcceptEncoding
    if (req.http.Accept-Encoding) {
        if (req.http.Accept-Encoding ~ "gzip") {
            set req.http.Accept-Encoding = "gzip";
        } elsif (req.http.Accept-Encoding ~ "deflate") {
            set req.http.Accept-Encoding = "deflate";
        } else {  
            # unknown algorithm  
            remove req.http.Accept-Encoding;
        }
    }
}
 
sub vcl_fetch {
    # static files always cached 
    if (req.url ~ "^/static") {
       unset beresp.http.set-cookie;
       return (deliver);  
    }
 
    # pass through for anything with a session/csrftoken set
    if (beresp.http.set-cookie ~ "sessionid" || beresp.http.set-cookie ~ "csrftoken") {
       return (pass);
    } else {
       return (deliver);
    }
}
