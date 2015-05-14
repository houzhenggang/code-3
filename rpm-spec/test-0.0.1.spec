Name:           sina-pserpm
Version:        0.0.1
Release:        el6%{?dist}
Summary:       	This is the rpm-like program without real installing. 

Group:        	System Environment/Libraries  
License:       	GPL 
URL:           	repos.sina.cn/sina/sina-sina-0.0.1.tar.gz 
Source0:        sina-pserpm-0.0.1.tar.gz


%description


%clean
rm -rf $RPM_BUILD_ROOT


%files
%{_bindir}/*
%{_usr}/share/*
%{_var}/lib/*

%changelog
