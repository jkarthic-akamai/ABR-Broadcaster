#!/bin/bash

set -e
set -o pipefail
if ! grep -q '^\s*LoadModule\s\+vhost_alias_module\s\+libexec/apache2/mod_vhost_alias.so' /etc/apache2/httpd.conf; then
  echo 'LoadModule vhost_alias_module libexec/apache2/mod_vhost_alias.so' | sudo tee -a /etc/apache2/httpd.conf;
fi

if ! grep -q '^\s*Include\s\+/private/etc/apache2/extra/httpd-vhosts.conf' /etc/apache2/httpd.conf; then
  echo 'Include /private/etc/apache2/extra/httpd-vhosts.conf' | sudo tee -a /etc/apache2/httpd.conf;
fi

if type mod_wsgi-express; then
  echo "Found mod_wsgi-express"
else
  echo "mod_wsgi-express not found. Trying copy to /usr/local/bin"
  sudo cp /Library/Frameworks/Python.framework/Versions/2.7/bin/mod_wsgi-express /usr/local/bin/
fi

mod_wsgi-express module-config > wsgi_config.txt
while IFS="" read -r p || [ -n "$p" ]
do
  if ! grep -q "$p" /etc/apache2/httpd.conf; then
    echo "$p" | sudo tee -a /etc/apache2/httpd.conf;
  fi
done < wsgi_config.txt
