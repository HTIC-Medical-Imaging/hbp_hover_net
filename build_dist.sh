
# copy only toplevel executable and dependent codes to dist

mkdir -p dist/misc 
cp step*.sh dist
cp entryPoint.sh dist
cp setup_db.py insert_db_records.py create_mmap.py dist
cp src/run_infer.py dist 
cp -r src/misc/*.py dist/misc
mkdir -p dist/infer
cp src/infer/*.py dist/infer
mkdir -p dist/dataloader 
cp src/dataloader/infer_loader.py dist/dataloader
cp -r src/models dist
cp -r src/run_utils dist
cp -r bin dist
cp -r lib dist
cp glymurrc dist
cp requirements.txt dist


