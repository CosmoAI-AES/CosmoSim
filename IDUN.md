
+ [Yum in User Space](https://stackoverflow.com/questions/36651091/how-to-install-packages-in-linux-centos-without-root-user-with-automatic-depen)

```
module purge
module load OpenCV/4.5.3-foss-2021a-contrib
module load CMake/3.20.1-GCCcore-10.3.0
```




## Intel Compiler

```
module purge
module load intel/2020b
module load SciPy-bundle/2020.11-intel-2020b
module load CMake/3.18.4-GCCcore-10.2.0
```

```
cmake -D CMAKE_C_COMPILER=icc -D CMAKE_CXX_COMPILER=icc ..
```

## Libraries in User space

```
export PATH="$HOME/local/usr/sbin:$HOME/local/usr/bin:$HOME/local/bin:$PATH"
export MANPATH="$HOME/local/usr/share/man:$MANPATH"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/local/usr/lib:$HOME/local/usr/lib64"
export LD_RUN_PATH="$LD_RUN_PATH:$HOME/local/usr/lib:$HOME/local/usr/lib64"
export CPATH=$CPATH:$HOME/local/usr/include
```


