%define major 4
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

Summary:	Gets a file from a FTP, GOPHER or HTTP server
Name:		curl
Version:	7.25.0
Release:	%mkrel 1
Epoch:		1
License:	BSD-like
Group:		Networking/Other
URL:		http://curl.haxx.se
Source0:	http://curl.haxx.se/download/%{name}-%{version}.tar.lzma
Source1:	http://curl.haxx.se/download/%{name}-%{version}.tar.lzma.asc
Patch3:		%{name}-7.21.5-privlibs.patch
Patch4:		%{name}-7.15.3-multilib.patch
Patch6:		%{name}-7.18.2-do-not-build-examples.patch
BuildRequires:	groff-for-man
BuildRequires:	openssl-devel
BuildRequires:	zlib-devel
BuildRequires:	libidn-devel
BuildRequires:	libssh2-devel
BuildRequires:	openldap-devel
BuildRequires:	krb5-devel
#BuildRequires:	c-ares-devel
# (misc) required for testing
BuildRequires:	stunnel
Provides:	webfetch
Requires:	%{libname} = %{epoch}:%{version}-%{release}

%description
curl is a client to get documents/files from servers, using any of the
supported protocols. The command is designed to work without user
interaction or any kind of interactivity.

curl offers a busload of useful tricks like proxy support, user
authentication, ftp upload, HTTP post, file transfer resume and more.

This version is compiled with SSL (https) support.

%package -n %{libname}
Summary:	A library of functions for file transfer
Group:		Networking/Other
%if %mdkversion >= 200700
Requires:	rootcerts >= 1:20070713.00
%endif

%description -n %{libname}
libcurl is a library of functions for sending and receiving files through
various protocols, including http and ftp.

You should install this package if you plan to use any applications that
use libcurl.

%package -n %{develname}
Summary:	Header files and static libraries for libcurl
Group:		Development/C
Requires:	%{libname} = %{epoch}:%{version}-%{release}
Provides:	%{name}-devel = %{epoch}:%{version}-%{release}
Provides:	lib%{name}-devel = %{epoch}:%{version}-%{release}
Provides:	libcurl%{major}-devel = %{epoch}:%{version}-%{release}
Obsoletes:	%mklibname %{name} 4 -d
Provides:	%mklibname %{name} 4 -d

%description -n %{develname}
libcurl is a library of functions for sending and receiving files through
various protocols, including http and ftp.

You should install this package if you wish to develop applications that
use libcurl.

%package examples
Summary:	Example files for %{name} development
Group:		Development/C
Requires:	%{develname} = %{epoch}:%{version}-%{release}

%description examples
Example files for %{name} development.

%prep
%setup -q
%patch3 -p1 -b .privlib~
%patch4 -p1 -b .multilib~
%patch6 -p1 -b .examples~

%build
autoreconf -fiv

%configure2_5x \
	--with-ssl \
	--without-gnutls \
	--with-zlib \
	--with-libidn \
	--with-ssh2 \
	--with-random \
	--enable-hidden-symbols \
	--enable-optimize \
	--enable-nonblocking \
	--enable-thread \
	--enable-crypto-auth \
	--enable-libgcc \
	--enable-ldaps \
	--enable-ipv6 \
	--with-ca-bundle=%{_sysconfdir}/pki/tls/certs/ca-bundle.crt \
	--with-gssapi=%{_prefix} \
	--disable-ares

# we don't want them in curl-examples:
%__rm -r docs/examples/.deps

%make

# disable tests that want to connect/run sshd, which is quite impossible
%check
%__make test TEST_Q='-a -p -v !SCP !SFTP !SOCKS4 !SOCKS5 !TFTP !198' 

%install
%__rm -rf %{buildroot}
%makeinstall_std 

# [july 2008] HACK. to be replaced by a real fix
%__sed -i -e 's!-Wl,--as-needed!!' -e 's!-Wl,--no-undefined!!' %{buildroot}%{_bindir}/%{name}-config
%__sed -i -e 's!-Wl,--as-needed!!' -e 's!-Wl,--no-undefined!!' %{buildroot}%{_libdir}/pkgconfig/*.pc

%multiarch_binaries %{buildroot}%{_bindir}/%{name}-config

# (tpg) use rootcerts's certificates #35917
find %{buildroot} -name ca-bundle.crt -exec rm -f '{}' \;

# nuke the libtool *.la file
%__rm -f %{buildroot}%{_libdir}/*.la

# nuke the static lib
%__rm -f %{buildroot}%{_libdir}/*.a

%clean
%__rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/curl
%{_mandir}/man1/curl.1*

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/*.so.%{major}*

%files -n %{develname}
%defattr(-,root,root)
%docdir docs/
%doc docs/BUGS docs/KNOWN_BUGS docs/CONTRIBUTE docs/FAQ CHANGES
%doc docs/FEATURES docs/RESOURCES docs/TODO docs/THANKS docs/INTERNALS
%{_bindir}/curl-config
%{multiarch_bindir}/curl-config
%{_libdir}/libcurl.so
%{_includedir}/curl
%{_libdir}/pkgconfig/*.pc
%{_mandir}/man1/curl-config.1*
%{_mandir}/man3/*

%files examples
%defattr(-,root,root,644)
%doc docs/examples
