Name:           sina-yum
Version:        0.0.1
Release:        el6%{?dist}
Summary:       	This is the yum-like program just with changing the out format.

Group:        	System Environment/Libraries  
License:       	GPL 
URL:           	repos.sina.cn/source/sina-yum-0.0.1.tar.gz
Source0:        sina-yum-0.0.1.tar.gz


%description


%clean
rm -rf $RPM_BUILD_ROOT


%files
%{_bindir}/*
%{_datadir}/*


%changelog
