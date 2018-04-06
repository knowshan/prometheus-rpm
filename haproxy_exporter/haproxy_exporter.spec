%define debug_package %{nil}

%if 0%{?_version:1}
%define         _verstr      %{_version}
%else
%define         _verstr      0.8.0
%endif

Name:    haproxy_exporter
Version: %{_verstr}
Release: 1%{?dist}
Summary: Haproxy exporter
License: ASL 2.0
URL:     https://github.com/prometheus/haproxy_exporter

Source0: https://github.com/prometheus/haproxy_exporter/releases/download/v%{version}/haproxy_exporter-%{version}.linux-amd64.tar.gz
Source1: haproxy_exporter.service
Source2: haproxy_exporter.default
Source3: haproxy_exporter.init

BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7
BuildRequires:  systemd-units
Requires:       systemd
%endif
Requires(pre): shadow-utils

%description

Simple server that scrapes HAProxy stats and exports them via HTTP for Prometheus consumption

%prep
%setup -q -n %{name}-%{version}.linux-amd64

%build
/bin/true

%install
mkdir -vp %{buildroot}/var/lib/prometheus
mkdir -vp %{buildroot}/usr/bin

%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7
mkdir -vp %{buildroot}/usr/lib/systemd/system
mkdir -vp %{buildroot}/etc/default
install -m 644 %{SOURCE1} %{buildroot}/usr/lib/systemd/system/%{name}.service
install -m 644 %{SOURCE2} %{buildroot}/etc/default/%{name}
%else
mkdir -p %{buildroot}/%{_initrddir}
cp %{SOURCE3} %{buildroot}/%{_initrddir}/%{name}
%endif

install -m 755 %{name} %{buildroot}/usr/bin/%{name}

%pre
getent group prometheus >/dev/null || groupadd -r prometheus
getent passwd prometheus >/dev/null || \
  useradd -r -g prometheus -d /var/lib/prometheus -s /sbin/nologin \
          -c "Prometheus services" prometheus
exit 0

%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7

%post
%systemd_post %{name}.service
%preun
%systemd_preun %{name}.service
%postun
%systemd_postun %{name}.service

%else
/sbin/chkconfig --add %{name}

%preun
if [ "$1" = 0 ] ; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi

%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/usr/bin/%{name}
%attr(755, prometheus, prometheus)/var/lib/prometheus

%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7
/usr/lib/systemd/system/%{name}.service
%config(noreplace) /etc/default/%{name}
%else
%{_initrddir}/%{name}
%endif
