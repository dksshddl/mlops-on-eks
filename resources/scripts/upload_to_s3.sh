bucket_name=dksshddl-cfn
archive_name=mlops

bucket_uri=s3://${bucket_name}/${archive_name}.tar.gz

# 1. clean up
rm -rf package && mkdir package
aws s3 rm $bucket_uri

cd ..
# 2. archive
tar -czf ${archive_name}.tar.gz ml-on-eks/

aws s3 cp ${archive_name}.tar.gz $bucket_uri
rm -f ${archive}.tar.gz