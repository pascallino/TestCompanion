CREATE database TestCompanion;
CREATE  user 'TestCompanion'@'localhost' identified by 'TestCompanion';
in case of alterations use 
ALTER USER 'TestCompanion'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL privileges on TestCompanion.* to 'TestCompanion'@'localhost';
FLUSH privileges;




