Name: ll-rpm-data
Version: 1.0
Release: 1
Summary: Project-owned bounded offline package teaching data
License: MIT
BuildArch: noarch
Source0: data.txt
Source1: report.conf
Source2: LICENSE
%description
Original local fixture, not a vendor package. No services or maintainer scripts.
%prep
%build
%install
mkdir -p %{buildroot}/usr/share/learning-lab-rpm %{buildroot}/etc/learning-lab-rpm %{buildroot}/usr/share/licenses/ll-rpm-data
install -m 0644 %{SOURCE0} %{buildroot}/usr/share/learning-lab-rpm/data.txt
install -m 0644 %{SOURCE1} %{buildroot}/etc/learning-lab-rpm/report.conf
install -m 0644 %{SOURCE2} %{buildroot}/usr/share/licenses/ll-rpm-data/LICENSE
%files
%defattr(-,root,root,-)
%dir /usr/share/learning-lab-rpm
/usr/share/learning-lab-rpm/data.txt
%dir /etc/learning-lab-rpm
%config(noreplace) /etc/learning-lab-rpm/report.conf
%license /usr/share/licenses/ll-rpm-data/LICENSE
%changelog
* Thu Jan 01 2026 Mike Buchanan - 1.0-1
- Original offline Learning Lab fixture.
