#!/bin/bash -l
#usage:
#python lnRNA_Pipeline_sh_generation.py
#      <directory with fastq files>
#      <directory to index files>
#      <directory to annotation files>

import sys
import os
from datetime import datetime

# !!!!Pipeline currently built for single end files!!!!

# Get the date to append to folder name, to prevent overwriting previous folders
today = datetime.now().strftime("%b-%d-%y_%T")

# Initialize variables to store arguments. Currently hardcoded directories, but can be changed to arguments
# fastq_dir = os.listdir(sys.argv[1])  # directory to fastq files
# fastq_dir = os.listdir('/restricted/projectnb/lasvchal/Deric/Lassadata')
fastq_dir = os.listdir('/restricted/projectnb/lasvchal/Deric/Marburgdata')
# fastq_files = sys.argv[1]  # string of directory to fastq files
# fastq_files = '/restricted/projectnb/lasvchal/Deric/Lassadata'
fastq_files = '/restricted/projectnb/lasvchal/Deric/Marburgdata'
# index_file = os.listdir(sys.argv[2])  # string of directory to index file
index_file = '/restricted/projectnb/lasvchal/Deric/MacaqueIndex/MMU '
# annotation_file = os.listdir(sys.argv[3])  # string of directory to annotation gff or gtf file
annotation_file = ' /restricted/projectnb/lasvchal/Emily/src/Macaca_Mulatta_genome/GCF_000772875.2_Mmul_8.0.1_genomic.gff > '

# store the file information in a dictionary with left reads, right reads, sample name
file_information = {}

# keep track of the key value
i = 1
for files in fastq_dir:
    left_file = files

    # this part will change depending on how the sample id is collected
    sampleid = files.split("_")[0]

    file_information[i] = [left_file, sampleid]
    i += 1

# Now start generating the output files in the directory python file is run in
cwd = os.getcwd()  # Get current directory
newpath = os.path.join(cwd, 'Pipeline_output_' + today)  # Create new top directory for output files
batch_submit = newpath + '/batch_submit'  # Directory to where the batch submit file will be place
output_dir = newpath + '/qsub_files'  # Directory to where the qsub files will be placed
filtered_fastq_dir = newpath + '/filtered_fastq'  # Output location of trimmed, filtered fastq files
tophat_dir = newpath + '/tophat_output'  # Output location of tophat .bam files
temp_bam = newpath + '/temporary_alignments'  # Output location of temporary .bam files
raw_counts = newpath + '/raw_counts'  # Stores htseq raw counts

if not os.path.exists(newpath):  # Check if top directory exists, if not create directory tree for storing files
    os.makedirs(newpath)
    os.makedirs(output_dir)  # directory for qsub files
    os.makedirs(batch_submit)  # directory for batch submit file
    os.makedirs(raw_counts)  # directory for filtered fastq
    os.makedirs(filtered_fastq_dir)  # directory for filtered fastq
    os.makedirs(tophat_dir)  # directory for filtered tophat .bam files
    os.makedirs(temp_bam)  # directory for temporary bam files
else:
    print "The directory already exists, exiting program"
    sys.exit()

# this information goes at the top of all the files
header = '''#!/bin/bash -l
#
#Run this file using 'qsub -P lasvchal example.qsub'

# All lines starting with "#$" are SGE qsub commands
#

# Specify which shell to use
#$ -S /bin/bash

# Run on the current working directory
#$ -cwd

#Finally, set the memory usage, the time limit, and the number of slots requested
#$ -l mem_total=64G
#$ -l h_rt=300:00:00
#$ -pe omp 8

###SEQUENCING PROCESSING STARTS HERE

#Load modules, order is important
module load fastx-toolkit/0.0.14
module load python2.7/Python-2.7.3_gnu446
module load boost/1.58.0
module load samtools/1.2
module load bowtie2/2.2.9
module load tophat/2.1.0
module load cufflinks/2.2.1
module load HTSeq/0.5.4p1_Python-2.7.3\n\n
'''
header2 = '''#!/bin/bash -l
# Usage: bash <directory to batch_submit.sh> <directory to .qsub files>
#
'''

# New file to batch submit qsub files
new_file2 = open(batch_submit + '/' + 'lncRNA_pipeline_batch_submit_' + today + '.sh', 'w')
new_file2.write(header2)
new_line2 = ''

# Create qsub files
for keys in file_information:
    sample_name = str(file_information[keys][0]).strip(".fastq")
    new_file = open(output_dir + '/' + sample_name + '.qsub', 'w')
    new_file.write(header)  # write the header information
    new_line = ''  # Initialize variable to store data

    # Write new qsub to batch submit
    new_line2 += 'qsub -P lasvchal ' + output_dir + '/' + sample_name + '.qsub\n'

    # unzip the file
    new_line += 'echo "Unzipping files"\n'
    new_line += 'gunzip ' + fastq_files + '/' + file_information[keys][0] + '\n\n'
    # new_line += 'gunzip ' + fastq_files + file_information[keys][1] + '\n'

    # filter files
    new_line += '#filter the poor quality reads\necho "Starting Quality Trimming"\n'

    # Reads fastq files and removes low quality reads
    new_line += 'fastq_quality_trimmer -i ' + fastq_files + '/' + file_information[keys][0].strip('.gz') + ' -o ' + \
                filtered_fastq_dir + '/' + file_information[keys][1] + '_R1_trimmed.fastq -t 20 -l 40 -Q 33 -v\n\n'

    new_line += 'echo "Starting Quality Filtering"\n'
    new_line += 'fastq_quality_filter -i ' + filtered_fastq_dir + '/' + \
                file_information[keys][1] + '_R1_trimmed.fastq -o ' + \
                filtered_fastq_dir + '/' + file_information[keys][1] + \
                '_R1_filtered.fastq -q 20 -p 80 -Q 33 -v\n\n'

    # Remove trimmed fastq files, comment out to keep files
    new_line += 'echo "Removing Fastq Trimmed files"\n'
    new_line += 'rm -f ' + filtered_fastq_dir + '/' + file_information[keys][1] + '_R1_trimmed.fastq\n\n'

    # Align to index
    new_line += 'echo "Aligning to genome"\n'
    tophat_sample_dir = tophat_dir + '/' + sample_name
    new_line += 'mkdir ' + tophat_sample_dir + '\n'  # Directory for tophat output files for each sample
    new_line += 'tophat -p 8 -o ' + tophat_sample_dir + ' ' + index_file + \
                filtered_fastq_dir + '/' + file_information[keys][1] + '_R1_filtered.fastq\n\n'

    # Remove filtered fastq files, comment out to keep files
    new_line += 'echo "Removing Fastq Filtered files"\n'
    new_line += 'rm -f ' + filtered_fastq_dir + '/' + file_information[keys][1] + '_R1_filtered.fastq\n\n'

    new_line += 'echo "Getting count Information"\n'

    # new_line += 'echo "Moving .bam files to one folder"\n'
    # new_line += 'cp ' + tophat_sample_dir + '/' + file_information[keys][1] + '/accepted_hits.bam ' + temp_bam + \
    #     file_information[keys][1] + '.bam\n'  # Copy .bam files to a temporary location

    # new_line += 'echo "Sorting .bam files"\n'
    # new_line += 'samtools sort -n -T ' + temp_bam + '/temp/' + file_information[keys][1] + '_temporary.bam -o ' + \
    #     temp_bam + file_information[keys][1] + '_temp.bam ' + temp_bam + \
    #     file_information[keys][1] + '.bam\n'  # sorts .bam files by name and renames them temp.bam

    # new_line += 'rm -f ' + temp_bam + file_information[keys][1] + '.bam\n'  # Remove temporary .bam files

    # Convert .bam file to .sam file for htseq count
    new_line += 'echo "Converting .bam files to .sam files"\n'
    new_line += 'samtools view -h -o ' + temp_bam + '/' + sample_name + '_temp.sam ' + \
                tophat_sample_dir + '/accepted_hits.bam\n\n'

    # new_line += 'echo "Removing temp.bam files"\n'
    # new_line += 'rm -f ' + temp_bam + '/temp/' + file_information[keys][1] + '_temp.bam\n\n'  # Remove temp.bam files

    # Count times a sequence matches a gene and output as txt file
    new_line += 'echo "htseq-count initialized"\n'
    new_line += 'htseq-count --stranded=no --type=ncRNA --idattr=gene ' \
                + temp_bam + '/' + sample_name + '_temp.sam' + \
                annotation_file + raw_counts + '/' + \
                sample_name + '.txt\n\n'

    # Remove temporary .sam files, comment out to keep files
    new_line += 'echo "Removing temp.sam files"\n'
    new_line += 'rm -f ' + temp_bam + '/' + sample_name + '_temp.sam\n\n'

    # new_line += 'samtools view -b -o ' + sys.argv[6] + '/' + file_information[keys][1] + '.bam ' + temp_bam + '/' + \
    #             file_information[keys][1] + '.sam\n'  # Convert .sam output from htseq-count to .bam files
    #
    # new_line += 'rm -f ' + temp_bam + '/' + file_information[keys][1] + '.sam\n'  # Remove .sam files

    new_line += 'echo "Count Collection Completed"\n\n\n'

    # write the commands to a qsub file
    new_file.write(new_line)

    # Close file
    new_file.close()

new_file2.write(new_line2)
new_file2.close()
print "####Qsub generation finished#####"
