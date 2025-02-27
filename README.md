# PIP pkgs required
- google-generativeai
- termcolor
- whois

# How to get API key?
Visit https://aistudio.google.com/app/apikey and click "generate"
I am not responsible for any cost associated with use of your API key

# Generate & check domains
Fist, you need to get API key. Then place it in key.conf. Edit domains.conf in `[tld]` section: place tlds you would like to check. Now you can use Option 2.

# Check domains from domains.conf
Place domain names you would like to check in `[d]` section. `[tld]` section is for tlds in which names should be checked.

# TLDs confirmed to work
- com
- net
- eu
- org
- dev
- me
- one
- ovh

Other will probably work, but may not
