$Long Non-coding RNA Pipeline
========

$This project is designed to search for known lncRNA in RNA-seq single end read data and provide count data as output

To use this project:
	!Currently the pipeline has the directories hardcoded, to use arguments uncomment appropriate lines (18-27)!
	1a. Enter directories for zipped fastq file, index file and annotation file as variables, then run in command line
		$ python lnRNA_Pipeline_sh_generation.py
	-or after uncommenting appropriate lines-
	1b. Input into command line, assuming you are in the same directory as the python file, with appropriate arguments:
		$ python lnRNA_Pipeline_sh_generation.py
			  <directory with zipped fastq files>
			  <directory to index files>
			  <directory to annotation files>
	2. Submit the batch submit file (.sh) created by the program to the shared computing cluster, found in Pipeline_output_[DATE]/batch_submit
		$ bash <lncRNA_pipeline_batch_submit_[DATE].sh>
Features
--------
- Creates a directory tree in the directory the python file is stored to store files created by pipeline
- Stores each run of the pipeline in a separate folder, differentiated by the date and time it was created
	* Sample Output *
	Pipeline_output_Aug-31-16_08:47:49
		tophat_output [stores each input fastq file in an individual folder]
			Sample_lane3_m9d9.R1.fastq.gz
				accepted_hits.bam
				etc...
			Sample_lane3_m6d5.R1.fastq.gz
			etc...
		temporary_alignments
			[storage for temporary .sam files created by samtools. Empty by default, can keep files by commenting rm command (line 178-179)]
		raw_counts [count output from htq-seq count]
			Sample_lane3_m9d9.R1.fastq.gz.txt
			etc...
		qsub_files [qsub files for submitting each individual fastq file's pipeline]
			Sample_lane3_m9d9.R1.fastq.gz.qsub
			etc...
		filtered_fastq
			[storage for temporary filtered fastq files created by fastx. Empty by default, can keep files by commenting rm command (line 146-147)]
		batch_submit [single .sh file, submits all qsub files to SCC]
			lncRNA_pipeline_batch_submit_Aug-31-16_08:47:49.sh
- Header sets memory usage, time limit, number of cores/slots requested
	#$ -l mem_total=64G # sets 64 gigs of memory
	#$ -l h_rt=300:00:00 # sets time limit as 300 hours, the maximum time
	#$ -pe omp 8 # sets number of cores as 8, same number as tophat requests
- Takes zipped fastq files or unzipped fastq files, (un)comment appropriate lines (117-118) to switch
- Filters fastq files using fastx-toolkit
	fastq_quality_trimmer is run with the following arguments:
		-t 20 Quality threshold - nucleotides with lower quality will be trimmed (from the end of the sequence)
		-l 40 Minimum length - sequences shorter than this (after trimming) will be discarded. Default = 0 = no minimum length.
		-Q 33 [Actually I'm unsure what this argument is, I copied it from Emily's code, can't find a reference in fastx-toolkit documentation]
	fastq_quality_filter is run with the following arguments:
		-q 20 Minimum quality score to keep.
		-p 80 Minimum percent of bases that must have [-q] quality.
		-Q 33 [Actually I'm unsure what this argument is, I copied it from Emily's code]
		-v    Verbose - report number of sequences.
- Aligns to index file using Tophat
	Currently uses requests 8 cores using argument -p 8
- Converts .bam files created by tophat to .sam files. 
	(Step is only neccessary for htseq-count Version 0.5.4, 0.6.0 added native .bam file support using --format)
- htseq-count counts reads
	searches for reads labelled ncRNA by the annotation file (--type=ncRNA)
	outputs as text file

Dependencies
------------

Python
	sys
	os
	datetime.datetime
Linux/Bash
	fastx-toolkit/0.0.14
	python2.7/Python-2.7.3_gnu446
	boost/1.58.0
	samtools/1.2
	bowtie2/2.2.9
	tophat/2.1.0
	cufflinks/2.2.1
	HTSeq/0.5.4p1_Python-2.7.3

Contribute
----------

- Source Code: github.com/hydriniumh2/lncRNA-pipeline.git

Support
-------

If you are having issues, please let me know.
My email is dezhang@bu.edu

License
-------

The project is licensed under the MIT license.