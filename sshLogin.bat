set w_strDirKey=%~dp0
set w_strKeyName=daily_report_web.pem
set w_strEC2User=ec2-user

ssh -i %w_strDirKey%\%w_strKeyName% ec2-user@ec2-35-78-186-87.ap-northeast-1.compute.amazonaws.com


