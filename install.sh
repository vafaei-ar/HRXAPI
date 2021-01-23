
URL='https://github.com/hirax-array/HIRAX-Shared-Simulations.git'

if [ ! -d HIRAX-Shared-Simulations ] ; then
    git clone "$URL"
fi


envname=hirax

if [ $(conda env list | grep $envname | wc -l) -ne 1 ]; then

cd HIRAX-Shared-Simulations/conda_environment/
conda env create -f environment.yml --name $envname
cd -

eval "$(conda shell.bash hook)"
conda activate $envname

pip install --upgrade pip
#pip install --upgrade jax jaxlib==0.1.57+cuda110 -f https://storage.googleapis.com/jax-releases/jax_releases.html
echo CONDA IS READY
else
eval "$(conda shell.bash hook)"
conda activate $envname
fi


#cd ..
#python patch.py 0
#cd -

#date
#drift-makeproducts run prod_params.yaml 
#date

#cd virajcpu
#./pipline.sh
#cd -

#cd check
#vsub -c "./pipline.sh" --name hiraxtest --mem 30000 --time 6:00:00 -N 16





#mkdir -p checkall/hirax/21cm_sims/double_freq
#cd checkall/hirax/21cm_sims/double_freq

#nside=512
#freqstart=550
#freqend=605
#nchannels=32

#for mode in foreground galaxy gaussianfg pointsource; do
#vsub -c "cora-makesky --nside ${nside} --freq ${freqstart} ${freqend} ${nchannels} --freq-mode edge --pol full --filename $mode.h5 $mode" --part dpt-EL7 --name 21cm-gpu --mem 30000 --time 6:00:00 -N 16
#done 

#cd checkall
#vsub -c "./pipline.sh" --part dpt-gpu-EL7 --name 21cm-gpu --mem 30000 --time 6:00:00 --ngpu 1
#cd -

#conda env remove --name hiraxtest
