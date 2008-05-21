#
Summary:	Web Based LDAP Administration Program
Name:		gosa
Version:	2.5.16.1
Release:	0.1
License:	GPL
Source0:	ftp://oss.gonicus.de/pub/gosa/%{name}-%{version}.tar.gz
# Source0-md5:	5bd315132e4962c228c32f00a68e8be8
Group:		Applications/Networking
URL:		http://oss.GONICUS.de/project/?group_id=6
Buildarch:	noarch
Requires:	ImageMagick
Requires:	php(imap)
Requires:	php(ldap)
Requires:	php(mbstring)
Requires:	php(mysql)
Requires:	php(snmp)
Requires:	webserver(php)
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}
%define		_sysconfdir	%{_webapps}/%{_webapp}
%define		_appdir		%{_datadir}/%{_webapp}


%description
GOsa is a combination of system-administrator and end-user web
interface, designed to handle LDAP based setups. Provided is access to
posix, shadow, samba, proxy, fax, and kerberos accounts. It is able to
manage the postfix/cyrus server combination and can write user adapted
sieve scripts.

%package schema
Summary:	Schema Definitions for the GOSA package
Group:		Applications/Networking
Requires:	openldap-servers >= 2.2.0
Obsoletes:	gosa-ldap

%description schema
Contains the Schema definition files for the GOSA admin package.

%package mkntpasswd
Summary:	Schema Definitions for the GOSA package
Group:		Applications/Networking
Requires:	perl-Crypt-SmbHash >= 0.02

%description mkntpasswd
Wrapper Script around perl to create Samba Hashes on the fly, added
for completeness only. If in doubt use sambas "native" mkntpwd tool to
generate hashes for GOsa.

%package help-en
Summary:	English online manual for GOSA package
Group:		Applications/Networking
Requires:	gosa >= %{version}

%description help-en
English online manual page for GOSA package

%package help-de
Summary:	German localized online manual for GOSA package
Group:		Applications/Networking
Requires:	gosa >= %{version}

%description help-de
German localized online manual page for GOSA package

%package help-fr
Summary:	French localized online manual for GOSA package
Group:		Applications/Networking
Requires:	gosa >= %{version}

%description help-fr
French localized online manual page for GOSA package

%package help-nl
Summary:	Dutch localized online manual for GOSA package
Group:		Applications/Networking
Requires:	gosa >= %{version}

%description help-nl
Dutch localized online manual page for GOSA package

%prep
%setup -q

cat > apache.conf <<'EOF'
Alias /%{name} %{_appdir}/html
<Directory %{_appdir}/html>
        Options None
        AllowOverride None
        Order allow,deny
        Allow from all
</Directory>
EOF

cat > lighttpd.conf <<'EOF'
alias.url += (
    "/%{name}" => "%{_appdir}/html",
)
EOF

%build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_datadir}/gosa

# Copy
DIRS="doc ihtml plugins html include locale"
for i in $DIRS; do \
cp -ua $i $RPM_BUILD_ROOT%{_datadir}/gosa/$i ; \
done
mkdir $RPM_BUILD_ROOT%{_bindir}
cp bin/mkntpasswd $RPM_BUILD_ROOT%{_bindir}/

# Create files for temporary stuff
for i in compile config cache; do \
  install -d $RPM_BUILD_ROOT/var/spool/gosa/$i ; \
done

# Cleanup manual dirs
for i in admin devel; do \
rm -rf $RPM_BUILD_ROOT%{_datadir}/gosa/doc/guide/$i ; \
done

# Remove (some) unneeded files
for i in gen_locale.sh gen_online_help.sh gen_function_list.php update.sh; do \
rm -rf $RPM_BUILD_ROOT%{_datadir}/gosa/$i ; \
done

# Cleanup guide
rm -rf $RPM_BUILD_ROOT%{_datadir}/gosa/doc/guide/user/*/lyx-source


# Copy default config
install -d $RPM_BUILD_ROOT%{confdir}

install -d $RPM_BUILD_ROOT%{_sysconfdir}/openldap/schema/gosa
mv contrib/openldap/*.schema $RPM_BUILD_ROOT%{_sysconfdir}/openldap/schema/gosa
sed 's§"CONFIG_TEMPLATE_DIR", "../contrib/"§"CONFIG_TEMPLATE_DIR", "%{docdir}/"§g' $RPM_BUILD_ROOT%{_datadir}/gosa/include/functions.inc > $RPM_BUILD_ROOT%{_datadir}/gosa/include/functions.inc.new
mv -f $RPM_BUILD_ROOT%{_datadir}/gosa/include/functions.inc.new $RPM_BUILD_ROOT%{_datadir}/gosa/include/functions.inc

mv -f doc manual
install -d $RPM_BUILD_ROOT%{_sysconfdir}/gosa/vacation
mv -f $RPM_BUILD_ROOT%{_datadir}/gosa/plugins/personal/mail/sieve-*.txt $RPM_BUILD_ROOT%{_sysconfdir}/gosa
install -d $RPM_BUILD_ROOT%{_docdir}/gosa-%{version}
rm -rf $RPM_BUILD_ROOT%{_datadir}/gosa/contrib

cp -a apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
cp -a apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
cp -a lighttpd.conf $RPM_BUILD_ROOT%{_sysconfdir}/lighttpd.conf

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerin -- lighttpd
%webapp_register lighttpd %{_webapp}

%triggerun -- lighttpd
%webapp_unregister lighttpd %{_webapp}

%clean
rm -rf $RPM_BUILD_ROOT

%post
# Add shells file to %{_sysconfdir}/gosa
/bin/cp /etc/shells %{_sysconfdir}

%pre
# Cleanup compile dir on updates, always exit cleanly even on errors
[ -d /var/spool/gosa ] && rm -rf /var/spool/gosa/* ; exit 0

%postun
# Remove temporary files, just to be sure
[ -d /var/spool/gosa ] && rm -rf /var/spool/gosa/* ; exit 0

%files
%defattr(644,root,root,755)
%doc AUTHORS README Changelog COPYING FAQ contrib/gosa.conf contrib/mysql contrib/scripts contrib/vacation_example.txt contrib/demo.ldif contrib/openldap
%dir %attr(750,root,http) %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lighttpd.conf
%config(noreplace) %attr(700,http,http) %{_sysconfdir}
%attr(700,http,http) /var/spool/gosa
%attr(744,http,http) %{_datadir}/gosa/html
%attr(744,http,http) %{_datadir}/gosa/ihtml
%attr(744,http,http) %{_datadir}/gosa/include
%attr(744,http,http) %{_datadir}/gosa/locale
%attr(744,http,http) %{_datadir}/gosa/plugins
%attr(744,http,http) %{_datadir}/gosa/doc/guide.xml

%files schema
%defattr(644,root,root,755)
%doc COPYING AUTHORS README contrib/demo.ldif contrib/openldap
%{_sysconfdir}/openldap/schema/gosa

%files mkntpasswd
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/mkntpasswd

%files help-en
%defattr(644,root,root,755)
%{_datadir}/gosa/doc/guide/user/en

%files help-de
%defattr(644,root,root,755)
%{_datadir}/gosa/doc/guide/user/de

%files help-fr
%defattr(644,root,root,755)
%{_datadir}/gosa/doc/guide/user/fr

%files help-nl
%defattr(644,root,root,755)
%{_datadir}/gosa/doc/guide/user/nl
