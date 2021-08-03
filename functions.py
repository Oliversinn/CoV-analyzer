import subprocess as sp
import os
import sys
import re

def align_fastq(fastq_r1, fastq_r2, reference, threads, output_directory, seq_name, programs_paths):
    print(programs_paths['bwa']+'bwa mem -t '+ threads + ' '+reference+' '+fastq_r1+' '+fastq_r2+ ' ' +
                            '| gzip > '+ output_directory+seq_name+'.mapped.sam.gz')
    mappingOutput=sp.check_output(programs_paths['bwa']+'bwa mem -t '+ threads + ' '+reference+' '+fastq_r1+' '+fastq_r2+ ' ' +
                            '| gzip > '+ output_directory+seq_name+'.mapped.sam.gz',
                            shell=True, stderr=sp.STDOUT)
    print('Done')
        
    ## error de no encuentra referencia 'fail to locate the index files'
    ## error de que no encuentra algún fastq 'fail to open file'

def bam_preprocess(RAM, output_directory, seq_name, programs_paths):
    print(programs_paths['gatk']+'gatk AddOrReplaceReadGroups -I '+output_directory+seq_name+'.mapped.sam.gz '+
                                '-O '+output_directory+seq_name+'.sorted.read_groups.bam -SO coordinate -RGLB NextSeq -RGPL illumina '+
                                '-RGPU barcode -RGSM '+seq_name)
    ARRGOutput=sp.check_output(programs_paths['gatk']+'gatk AddOrReplaceReadGroups -I '+output_directory+seq_name+'.mapped.sam.gz '+
                                '-O '+output_directory+seq_name+'.sorted.read_groups.bam -SO coordinate -RGLB NextSeq -RGPL illumina '+
                                '-RGPU barcode -RGSM '+seq_name,
                                shell=True, stderr=sp.STDOUT)
    print('Done')

    print(programs_paths['samtools']+'samtools index '+output_directory+seq_name+'.sorted.read_groups.bam')
    indexOutput=sp.check_output(programs_paths['samtools']+'samtools index '+output_directory+seq_name+'.sorted.read_groups.bam',
                                shell=True, stderr=sp.STDOUT)
    print('Done')
    print(programs_paths['gatk']+'gatk --java-options "-Xmx'+RAM+'g"'+ 
                           ' SortSam -I '+output_directory+seq_name+'.sorted.read_groups.bam -O '+output_directory+seq_name+'.gatkSorted.bam -SO coordinate')
    gatkSorOutput=sp.check_output(programs_paths['gatk']+'gatk --java-options "-Xmx'+RAM+'g"'+ 
                           ' SortSam -I '+output_directory+seq_name+'.sorted.read_groups.bam -O '+output_directory+seq_name+'.gatkSorted.bam -SO coordinate',
                           shell=True, stderr=sp.STDOUT)
    print('Done')
    print(programs_paths['gatk']+'gatk --java-options "-Xmx'+RAM+'g"'+
                            ' MarkDuplicatesWithMateCigar -I '+output_directory+seq_name+'.gatkSorted.bam -O '+output_directory+seq_name+'.flagstat.bam '+
                            '-M '+output_directory+seq_name+'.marked_dup_metrics.txt --MINIMUM_DISTANCE -1 --CREATE_INDEX true')
    markedDuplicatesOutput=sp.check_output(programs_paths['gatk']+'gatk --java-options "-Xmx'+RAM+'g"'+
                            ' MarkDuplicatesWithMateCigar -I '+output_directory+seq_name+'.gatkSorted.bam -O '+output_directory+seq_name+'.flagstat.bam '+
                            '-M '+output_directory+seq_name+'.marked_dup_metrics.txt --MINIMUM_DISTANCE -1 --CREATE_INDEX true',
                            shell=True, stderr=sp.STDOUT)
    print('Done')
    print(programs_paths['samtools']+'samtools flagstat '+output_directory+seq_name+'.flagstat.bam > '+ output_directory+seq_name+'.flagstat')
    flagstatOutput=sp.check_output(programs_paths['samtools']+'samtools flagstat '+output_directory+seq_name+'.flagstat.bam > '+ output_directory+seq_name+'.flagstat',
                            shell=True, stderr=sp.STDOUT)
    print('Done')

def variant_calling(RAM, reference, output_directory, seq_name, programs_paths):
    print(programs_paths['gatk']+'gatk --java-options "-Xmx'+RAM+'g"'+
                            ' HaplotypeCaller -R '+reference+' -I '+output_directory+seq_name+'.flagstat.bam'+
                            ' -mbq 10 -ploidy 1 -O '+output_directory+seq_name+'.vcf')
    VCFoutput=sp.check_output(programs_paths['gatk']+'gatk --java-options "-Xmx'+RAM+'g"'+
                            ' HaplotypeCaller -R '+reference+' -I '+output_directory+seq_name+'.flagstat.bam'+
                            ' -mbq 10 -ploidy 1 -O '+output_directory+seq_name+'.vcf',
                            shell=True, stderr=sp.STDOUT)
    print('Done')
