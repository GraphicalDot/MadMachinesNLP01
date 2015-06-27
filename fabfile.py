


#!/usr/bin/env python

from __future__ import with_statement
from fabric.api import task, show, local, settings, prefix, abort, run, cd, env, require, hide, execute, put
from fabric.contrib.console import confirm
from fabric.network import disconnect_all
from fabric.colors import green as _green, yellow as _yellow, red as _red
from fabric.contrib.files import exists
from fabric.utils import error
import os
import time
from fabric.operations import local as lrun, run
"""
env.use_ssh_config = True
env.hosts = ["52.24.208.205"] ##For t2 medium
#env.hosts = ["ec2-54-186-203-98.us-west-2.compute.amazonaws.com"] ##For m3.large
env.user = "ubuntu"
env.key_filename = "/home/kaali/Programs/Python/MadMachinesNLP01/MadMachines.pem"
env.warn_only = True

This is the file which remotely makes an ec2 instance for the use of this repository
"""

VIRTUAL_ENVIRONMENT = "/home/{0}/VirtualEnvironment".format(env["user"])
print VIRTUAL_ENVIRONMENT

PATH = "/home/{0}/VirtualEnvironment/Canworks/".format(env["user"])
print PATH

TAGGERS_PATH = "{0}/Text_Processing/PosTaggers/hunpos-1.0-linux".format(PATH)

@task
def basic_setup():
	""""
	This method should be run before installing virtual environment as it will install python pip
	required to install virtual environment
	"""
	#run("sudo apt-get update")
	#run("sudo apt-get upgrade")
	env.run("sudo apt-get install -y python-pip")
        env.run("sudo apt-get install -y libevent-dev")
	env.run("sudo apt-get install -y python-all-dev")
	env.run("sudo apt-get install -y ipython")
	env.run("sudo apt-get install -y libxml2-dev")
	env.run("sudo apt-get install -y libxslt1-dev") 
	env.run("sudo apt-get install -y python-setuptools python-dev build-essential")
	"""
        run("sudo apt-get install -y libxml2-dev libxslt1-dev lib32z1-dev")
	run("sudo apt-get install -y python-lxml")
	#Dependencies for installating sklearn
	run("sudo apt-get install -y build-essential python-dev python-setuptools libatlas-dev libatlas3gf-base")
	#Dependencies for installating scipy
	run("sudo apt-get install -y liblapack-dev libatlas-dev gfortran")
	run("sudo apt-get install -y libatlas-base-dev gfortran build-essential g++ libblas-dev")
	#Dependicies to install hunpostagger
	run("sudo apt-get install -y ocaml-nox")
	run("sudo apt-get install -y mercurial")
	run("sudo apt-get install -y libpq-dev")
        run("sudo apt-get install build-essential libssl-dev libffi-dev python-dev")
        """

@task
def localhost():
        env.run = lrun
        env.hosts = ['localhost']

@task
def remote():
        env.run = run
        env.hosts = ['192.168.1.5']

def installing_riak():
        run("sudo apt-get install curl")
        run("sudo curl -s https://packagecloud.io/install/repositories/basho/riak/script.deb.sh | sudo bash")
        run("sudo apt-get install riak=2.1.1-1")
        
        

def increasing_ulimits():
        """
        /etc/security/limits.conf

        *     soft    nofile          40000
        *     hard    nofile          40000
        """
        return

def install_phantomjs():
        """
        http://phantomjs.org/build.html
        """
        run ("sudo apt-get install build-essential g++ flex bison gperf ruby perl \
                  libsqlite3-dev libfontconfig1-dev libicu-dev libfreetype6 libssl-dev \
                    libpng-dev libjpeg-dev python libX11-dev libxext-dev")
        run("sudo apt-get install ttf-mscorefonts-installer")
        run("git clone git://github.com/ariya/phantomjs.git")
        run("cd phantomjs")
        run("git checkout 2.0")
        run("./build.sh")


def install_elastic_search_stack():
        """
        For more configuration options for Elastic search, read the following document
        https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-4-on-ubuntu-14-04
        """
        env.run("sudo add-apt-repository -y ppa:webupd8team/java")
        env.run("sudo apt-get update")
        env.run("sudo apt-get -y install oracle-java8-installer")
        env.run("wget -O - http://packages.elasticsearch.org/GPG-KEY-elasticsearch | sudo apt-key add -")
        env.run("echo 'deb http://packages.elasticsearch.org/elasticsearch/1.4/debian stable main' | sudo tee /etc/apt/sources.list.d/elasticsearch.list")
        env.run("sudo apt-get update")
        env.run("sudo apt-get -y install elasticsearch=1.4.4")
        with cd("/usr/share/elasticsearch"):
                env.run("bin/plugin -install elasticsearch/elasticsearch-analysis-phonetic/2.4.3")
        env.run("sudo service elasticsearch start")


def get_host():
        if env["host"] == "localhost":
                print "We are on localhost"
        else:
                print env["host"], env["user"]

def virtual_env():
	"""
	This method installs the virual environment and after installing virtual environment installs the git.
	After installing the git installs the reuiqred repository
	"""
        if not exists(VIRTUAL_ENVIRONMENT, use_sudo=True):
	        run("virtualenv VirtualEnvironment")
                with cd(VIRTUAL_ENVIRONMENT):
                        put(PATH, VIRTUAL_ENVIRONMENT)
                        with prefix("source bin/activate"):
			        if confirm("Do you want to install requirements.txt again??"):
		                        run("pip install numpy==1.9.2")
                                        run("pip install -r Canworks/requirements.txt")



def install_text_sentence():
	"""
	If installs by pip shows an error"
	"""
	
        with cd(VIRTUAL_ENVIRONMENT):
		if not exists("text-sentence", use_sudo=True):	
			run ("sudo hg clone https://bitbucket.org/trebor74hr/text-sentence")
		
                with prefix("source bin/activate"):
                        run("ls")
			run("pip freeze")
                        with prefix("cd text-sentence"):
                            run("sudo {0}/bin/python setup.py install".format(VIRTUAL_ENVIRONMENT))


def download_corpora():
	with cd(VIRTUAL_ENVIRONMENT):
		with prefix("source bin/activate"):
                        run("pip freeze")
			print(_yellow("Now downloading textblob packages"))	
			run("python -m textblob.download_corpora")
			print(_green("Finished Downloading and installing textblob packages"))	
			
	with cd(VIRTUAL_ENVIRONMENT):
		with prefix("source bin/activate"):
                        print(_yellow("Now downloading nltk packages"))	
		        run("sudo {0}/bin/python -m nltk.downloader all".format(VIRTUAL_ENVIRONMENT))
			print(_yellow("Now downloading textblob packages"))	

def change_permission_api():
	with cd(PATH):
            run("sudo chmod 755 *")
            run("sudo chown {0}:{0} *".format(env["user"]))
       
        with cd(TAGGERS_PATH):
            run("sudo chmod 755 *")


def mongo():
	"""
	This method installs the mongodb database on the remote server.It after installing the mongodb replaces the 
	mongodb configuration with the one available in the git repository.
	"""
	with prefix("cd /home/ubuntu/VirtualEnvironment"):
		run("sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10")
		run("echo -e 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list")
		run("sudo apt-get update")
		run("sudo apt-get install -y mongodb-10gen")
	run("sudo rm -rf  /var/lib/mongodb/mongod.lock")
	run("sudo service mongodb restart")



def mongo_restore(dump):
        """
        """
        with cd(PATH):
                run("sudo mongorestore 21-feb")

def deploy():
	execute(basic_setup)
        #execute(virtual_env)
	#execute(install_text_sentence)
        #execute(download_corpora)
        #execute(change_permission_api)
        #execute(mongodb)
        #execute(mongo_restore)

