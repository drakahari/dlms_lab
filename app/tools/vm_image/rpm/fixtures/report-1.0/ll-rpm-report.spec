Name: ll-rpm-report
Version: 1.0
Release: 1
Summary: Project-owned bounded offline package teaching report
License: MIT
BuildArch: noarch
Requires: ll-rpm-data = 2.0-1
Source0: ll-rpm-report
Source1: LICENSE
%description
Original local report fixture. No services, scriptlets, triggers or accounts.
%prep
%build
%install
mkdir -p %{buildroot}/usr/bin %{buildroot}/usr/share/licenses/ll-rpm-report
install -m 0755 %{SOURCE0} %{buildroot}/usr/bin/ll-rpm-report
install -m 0644 %{SOURCE1} %{buildroot}/usr/share/licenses/ll-rpm-report/LICENSE
%files
%defattr(-,root,root,-)
/usr/bin/ll-rpm-report
%license /usr/share/licenses/ll-rpm-report/LICENSE
%changelog
* Thu Jan 01 2026 Mike Buchanan - 1.0-1
- Original offline Learning Lab fixture.
