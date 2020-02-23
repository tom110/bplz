for file in `ls | grep '.*z[0-9][0-9]$'`
do
 newfile=`echo $file | sed 's/\./%/g'`.zip
 mv $file $newfile
done