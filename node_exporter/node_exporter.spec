%define debug_package %{nil}

%if 0%{?_version:1}
%define         _verstr      %{_version}
%else
%define         _verstr      0.15.2
%endif

Name:    node_exporter
Version: %{_verstr}
Release: 1%{?dist}
Summary: Prometheus exporter for machine metrics, written in Go with pluggable metric collectors.
License: ASL 2.0
URL:     https://github.com/prometheus/node_exporter

Source0: https://github.com/prometheus/node_exporter/releases/download/v%{version}/node_exporter-%{version}.linux-amd64.tar.gz
Source1: node_exporter.service
Source2: node_exporter.default
Source3: node_exporter.init

BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7
BuildRequires:  systemd-units
Requires:       systemd
%endif
Requires(pre): shadow-utils

%description

Prometheus exporter for machine metrics, written in Go with pluggable metric collectors.

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
%systemd_post node_exporter.service
%preun
%systemd_preun node_exporter.service
%postun
%systemd_postun node_exporter.service

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
/usr/bin/node_exporter
%attr(755, prometheus, prometheus)/var/lib/prometheus

%if 0%{?fedora} >= 14 || 0%{?rhel} >= 7
/usr/lib/systemd/system/node_exporter.service
%config(noreplace) /etc/default/node_exporter
%else
%{_initrddir}/%{name}
%endif

