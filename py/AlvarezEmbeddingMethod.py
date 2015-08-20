# coding: utf-8


"""
Created on Thu Jul 23 2015

@author: Anton at 0x0af@ukr.net
"""

import math

import numpy
import scipy
from pyevolve import Crossovers, Mutators, Selectors, G1DBinaryString, GSimpleGA
from PIL import Image


def alvarez_embed(grayscale_container_path, binary_watermark_path, watermarked_image_path):
    """    
    Alvarez embedding method implementation. 
    
    Outputs the resulting watermarked image to watermarked_image_path
    
    23-July-2015
    """

    binary_watermark_1darray = numpy.asarray(genetic_algorithm_pretreatment(binary_watermark_path))
    m = int(math.sqrt(binary_watermark_1darray.shape[0]))

    grayscale_container_2darray = numpy.asarray(Image.open(grayscale_container_path).convert("L"))
    while grayscale_container_2darray.shape[0] != grayscale_container_2darray.shape[1]:
        if grayscale_container_2darray.shape[0] > grayscale_container_2darray.shape[1]:
            grayscale_container_2darray = numpy.c_[
                grayscale_container_2darray, numpy.zeros(grayscale_container_2darray.shape[0])]
        elif grayscale_container_2darray.shape[0] < grayscale_container_2darray.shape[1]:
            grayscale_container_2darray = numpy.r_[
                grayscale_container_2darray, numpy.zeros(grayscale_container_2darray.shape[1])[numpy.newaxis]]

    n = grayscale_container_2darray.shape[0]

    # Now try to find a normalized Hadamard matrix of size 4t closest to floor(n/m)

    hadamard_matrix_size = int(math.floor(float(n) / float(m)))

    hadamard_matrix_size_right = hadamard_matrix_size
    hadamard_matrix_size_left = hadamard_matrix_size

    # Find hadamard_matrix_size as an integer, divisible by 4 and a power of 2 and bigger than m/n
    while (hadamard_matrix_size_right % 4 != 0) or (
                (hadamard_matrix_size_right & (hadamard_matrix_size_right - 1)) != 0):
        hadamard_matrix_size_right += 1

    # Find hadamard_matrix_size as an integer, divisible by 4 and a power of 2 and less than m/n
    while (hadamard_matrix_size_left % 4 != 0) or ((hadamard_matrix_size_left & (hadamard_matrix_size_left - 1)) != 0):
        hadamard_matrix_size_left -= 1

    # Pick the closest or the least if equally distant
    if hadamard_matrix_size_right - hadamard_matrix_size < hadamard_matrix_size - hadamard_matrix_size_left:
        hadamard_matrix_size = hadamard_matrix_size_right
    else:
        hadamard_matrix_size = hadamard_matrix_size_left

    # print 'Hadamard matrix size: ', hadamard_matrix_size

    H = scipy.linalg.hadamard(hadamard_matrix_size)

    # print 'Hadamard matrix H: ', H

    block_size = int(math.floor(float(n) / float(m)))

    for i in range(0, m * m - 1):
        col_index = i % (n / block_size)
        row_index = i / (n / block_size)
        A = grayscale_container_2darray[col_index * block_size:col_index * block_size + hadamard_matrix_size,
            row_index * block_size:row_index * block_size + hadamard_matrix_size]
        # if i == 0 :
        #    print A
        B = numpy.dot(numpy.dot(H, A), H.transpose()) / hadamard_matrix_size
        # if i == 0 :
        #    print B
        b1 = B[3][3]
        b2 = B[3][5]
        # let b equal hadamard_matrix_size/4, as proposed by authors in 3.1 -> 1
        b = hadamard_matrix_size / 4
        d = abs((b1 - b2) / 2)
        if binary_watermark_1darray[i]:
            B[3][3] = b1 - d - b
            B[3][5] = b2 + d + b
        else:
            B[3][3] = b1 + d + b
            B[3][5] = b2 - d - b
        A = numpy.dot(numpy.dot(H.transpose(), B), H) / hadamard_matrix_size
        # After HT, some values are more than 255 and less than 0, so fix it
        A[A > 255] = 255
        A[A < 0] = 0
        # if i == 0 :
        #    print A
        grayscale_container_2darray[col_index * block_size:col_index * block_size + hadamard_matrix_size,
        row_index * block_size:row_index * block_size + hadamard_matrix_size] = A

    watermarked_image = Image.fromarray(numpy.uint8(grayscale_container_2darray))
    # watermarked_image.show()

    # Write image to file

    watermarked_image.save(watermarked_image_path)

    return


def alvarez_extract(grayscale_stego_path, extracted_watermark_path, watermark_size):
    """
    Alvarez extracting method implementation.
    
    Outputs the extracted watermark to extracted_watermark_path
    
    23-July-2015
    """

    grayscale_stego_2darray = numpy.asarray(Image.open(grayscale_stego_path).convert("L"))
    assert grayscale_stego_2darray.shape[0] == grayscale_stego_2darray.shape[1], 'Grayscale Stego is not square!'

    n = grayscale_stego_2darray.shape[0]
    m = watermark_size

    # Now try to find a normalized Hadamard matrix of size 4t closest to floor(n/m)

    hadamard_matrix_size = int(math.floor(float(n) / float(m)))

    hadamard_matrix_size_right = hadamard_matrix_size
    hadamard_matrix_size_left = hadamard_matrix_size

    # Find hadamard_matrix_size as an integer, divisible by 4 and a power of 2 and bigger than m/n
    while (hadamard_matrix_size_right % 4 != 0) or (
                (hadamard_matrix_size_right & (hadamard_matrix_size_right - 1)) != 0):
        hadamard_matrix_size_right += 1

    # Find hadamard_matrix_size as an integer, divisible by 4 and a power of 2 and less than m/n
    while (hadamard_matrix_size_left % 4 != 0) or ((hadamard_matrix_size_left & (hadamard_matrix_size_left - 1)) != 0):
        hadamard_matrix_size_left -= 1

    # Pick the closest or the least if equally distant
    if hadamard_matrix_size_right - hadamard_matrix_size < hadamard_matrix_size - hadamard_matrix_size_left:
        hadamard_matrix_size = hadamard_matrix_size_right
    else:
        hadamard_matrix_size = hadamard_matrix_size_left

    # print 'Hadamard matrix size: ', hadamard_matrix_size

    H = scipy.linalg.hadamard(hadamard_matrix_size)

    # print 'Hadamard matrix H: ', H

    block_size = int(math.floor(float(n) / float(m)))

    extracted_watermark = numpy.zeros(m * m)

    for i in range(0, m * m - 1):
        col_index = i % (n / block_size)
        row_index = i / (n / block_size)
        A = grayscale_stego_2darray[col_index * block_size:col_index * block_size + hadamard_matrix_size,
            row_index * block_size:row_index * block_size + hadamard_matrix_size]
        # if i == 0 :
        #    print A
        B = numpy.dot(numpy.dot(H, A), H.transpose()) / hadamard_matrix_size
        # if i == 0 :
        #    print B
        b1 = B[3][3]
        b2 = B[3][5]
        extracted_watermark[i] = 255 if b1 > b2 else 0

    extracted_watermark_image = Image.fromarray(numpy.uint8(extracted_watermark.reshape(m, m)))

    # Write image to file

    extracted_watermark_image.save(extracted_watermark_path)

    return


def genetic_algorithm_pretreatment(binary_watermark):
    """
    Steady-State genetic algorithm pretreatment implementation to get the most uncorrelated binary watermark permutation
    
    Outputs the permuted watermark vector
    
    23-July-2015
    """

    binary_watermark_2darray = numpy.asarray(Image.open(binary_watermark).convert("1"))
    assert (
        binary_watermark_2darray.shape[0] == binary_watermark_2darray.shape[1]), 'Error. Binary Watermark is not square'

    # Open binary watermark image with PIL, read it as a 1D array with numpy
    binary_watermark_1darray = numpy.ravel(numpy.asarray(Image.open(binary_watermark).convert("1")))

    def normalised_correlation(binary_vector, chromosome):
        cross = 0
        sq1 = 0
        sq2 = 0
        for x in xrange(0, binary_vector.size):
            cross += binary_vector[x] * chromosome[x]
            sq1 += binary_vector[x] * binary_vector[x]
            sq2 += chromosome[x] * chromosome[x]
        n_c = cross / math.sqrt(sq1) / math.sqrt(sq2)
        return n_c

    def eval_func(chromosome):
        score = 1 / normalised_correlation(binary_watermark_1darray, chromosome)
        # print 'Current chromosome score: ',score
        return score

    genome = G1DBinaryString.G1DBinaryString(binary_watermark_1darray.size)
    genome.evaluator.set(eval_func)
    genome.crossover.set(Crossovers.G1DBinaryStringXSinglePoint)
    genome.mutator.set(Mutators.G1DBinaryStringMutatorFlip)
    genome.setParams(rangemin=0, rangemax=1)
    ga = GSimpleGA.GSimpleGA(genome)
    ga.selector.set(Selectors.GRankSelector)
    ga.setGenerations(50)
    ga.setPopulationSize(20)
    ga.evolve(freq_stats=1)

    print 'Best individual NC: ', 1 / eval_func(ga.bestIndividual())

    permuted_binary_watermark = numpy.zeros(binary_watermark_1darray.size)

    for i in range(0, binary_watermark_1darray.size):
        permuted_binary_watermark[i] = ga.bestIndividual()[i]

    return permuted_binary_watermark


alvarez_embed("..\\steganography-embedding\\bmp\GrayscaleContainer.bmp",
              "..\\steganography-embedding\\bmp\BinaryWatermark.bmp",
              "..\\steganography-embedding\\bmp\Alvarez_Watermarked_Image.bmp")

alvarez_extract("..\\steganography-embedding\\bmp\Alvarez_Watermarked_Image.bmp",
                "..\\steganography-embedding\\bmp\Alvarez_Extracted_Binary_Watermark.bmp", 100)
