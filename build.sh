# Build process for lightgest and lightserve. We need to
# clone in the latest lightcurvedb and soauth.

echo "Creating ${1}"

python3 -m build .
cp dist/lightserve*.whl .

git clone https://github.com/simonsobs/soauth
git clone https://github.com/simonsobs/lightcurvedb

cd soauth
python3 -m build .
cp dist/soauth-*.whl ..
cd ..

cd lightcurvedb
python3 -m build .
cp dist/lightcurvedb-*.whl ..
cd ..

rm -rf soauth
rm -rf lightcurvedb

docker buildx build --platform=linux/amd64 -t $1 . 

wait

rm soauth-*.whl
rm lightcurvedb-*.whl
rm lightserve-*.whl
rm dist/*