#!/usr/bin/env python
import boto3

import subprocess
import sys
import json
import hashlib
import re
import os

from utils import *

class S3Bucket(object):
    """Convenience methods for S3 buckets"""

    def __init__(self, session, name):
        resource = session.resource('s3')
        self.bucket = resource.Bucket(name)
        self.name = name

    def info(self):
        """returns all the md5 values from the given s3 bucket."""
        return dict((o.key,{"Key": o.key, "Size": o.size, "ETag": o.e_tag})
                    for o in self.bucket.objects.all())

    def set_mimetype(self, key, mime):
        self.bucket.copy({'Bucket': self.name,
                          'Key': key}, key, ExtraArgs={'ContentType': mime})

    def delete_objects(self, objs):
        if len(objs) == 0:
            return
        obj_list = [ {"Key": obj} for obj in objs ]
        print ('bucket.delete_objects(Delete={"Objects":%s, "Quiet":False})' %
               repr(obj_list))
        self.bucket.delete_objects(
            Delete={"Objects":obj_list, "Quiet":False})

    def put_objects(self, objs):
        for obj in objs:
            mime_type = my_guess_mimetype(obj)
            f = open(obj)
            print ("bucket.put_object(Key=%s, Body=f, ContentType=%s)" %
                   (repr(obj), repr(mime_type)))
            self.bucket.put_object(Key=obj, Body=f, ContentType=mime_type)

##############################################################################
            
def local_info():
    result = {}
    local_files_to_check = find_files()
    for f in local_files_to_check:
        h = hashlib.md5()
        h.update(open(f).read())
        result[f[2:]] = {"ETag": h.hexdigest()}
    return result

def main():
    try:
        target_bucket_name = sys.argv[1]
        target_bucket = 's3://%s/' % target_bucket_name
        debug=True
    except KeyError:
        print "Expected path for target bucket"
        exit(1)

    session = boto3.Session(profile_name=os.environ["IEEEVIS_AWS_USER"])
    bucket = S3Bucket(session, target_bucket_name)

    print "Syncing with", target_bucket_name

    diff = diff_local_remote_buckets(local_info(), bucket.info())

    files_to_upload = diff['to_insert'] + diff['to_update']
    print "Uploading %s files:" % len(files_to_upload)
    for o in files_to_upload:
        print "  %s" % o
    bucket.put_objects(files_to_upload)

    files_to_remove = diff['to_delete']
    print "Removing %s files:" % len(files_to_remove)
    for o in files_to_remove:
        print "  %s" % o
    bucket.delete_objects(files_to_remove)

    files_to_keep = diff['same']
    print "Not touching %s other files." % len(files_to_keep)
    # for o in files_to_keep:
    #     print "  %s" % o
    
    print "Done!"

if __name__ == '__main__':
    main()
