#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  busca.py
#
#  Copyright 2014 juhegue 01/02/2015
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
"""Busca cadena en fichero/s del directorio
SINOPSIS
   busca.py [-b --binario][-c --cadena=]  [-d --dir=]  [-e --excluir]
            [-f --final=] [-h --help]     [-i --ignora][-o --oculto]
            [-p --palabra][-r --recursivo][-x --color] [-y --reemplaza]
OPCIONES
   -b     Busca en ficheros binarios.
   -c     Cadena a buscar.
   -d     Directorio a recorrer (sino el actual).
   -e     Excluir ficheros que terminen con la/s cadena/s dada.
   -f     Solo muestra los ficheros que terminen con la/s cadena/s dada.
   -h     Muestra la ayuda.
   -i     Ignora mayusculas/minusculas.
   -o     Busca en ficheros ocultos.
   -p     Solo palabra.
   -r     Recursivo.
   -x     Sin colores.
   -y     Reemplaza.
"""

import sys
import getopt
import os
import codecs

try:
    from binaryornot.check import is_binary
except:
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    def is_binary(fic):
        return is_binary_string(open(fic, 'rb').read(1024))

try:
    from termcolor import colored
except:
    # https://pypi.org/project/termcolor/
    ATTRIBUTES = dict(
        list(zip([
            'bold',
            'dark',
            '',
            'underline',
            'blink',
            '',
            'reverse',
            'concealed'
            ],
            list(range(1, 9))
            ))
        )
    del ATTRIBUTES['']


    HIGHLIGHTS = dict(
        list(zip([
            'on_grey',
            'on_red',
            'on_green',
            'on_yellow',
            'on_blue',
            'on_magenta',
            'on_cyan',
            'on_white'
            ],
            list(range(40, 48))
            ))
        )


    COLORS = dict(
        list(zip([
            'grey',
            'red',
            'green',
            'yellow',
            'blue',
            'magenta',
            'cyan',
            'white',
            ],
            list(range(30, 38))
            ))
        )


    RESET = '\033[0m'


    def colored(text, color=None, on_color=None, attrs=None):
        """Colorize text.

        Available text colors:
            red, green, yellow, blue, magenta, cyan, white.

        Available text highlights:
            on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white.

        Available attributes:
            bold, dark, underline, blink, reverse, concealed.

        Example:
            colored('Hello, World!', 'red', 'on_grey', ['blue', 'blink'])
            colored('Hello, World!', 'green')
        """
        if os.getenv('ANSI_COLORS_DISABLED') is None:
            fmt_str = '\033[%dm%s'
            if color is not None:
                text = fmt_str % (COLORS[color], text)

            if on_color is not None:
                text = fmt_str % (HIGHLIGHTS[on_color], text)

            if attrs is not None:
                for attr in attrs:
                    text = fmt_str % (ATTRIBUTES[attr], text)

            text += RESET
        return text

letras_digitos = ([chr(i) for i in range(ord("0"), ord("9")+1)])
letras_digitos += ([chr(i) for i in range(ord("A"), ord("Z")+1)])
letras_digitos += ([chr(i) for i in range(ord("a"), ord("z")+1)])
letras_digitos += ["_"]


def buscapalabra(cadena, linea, busca):
    ok = True
    if busca:
        ok = False
        pos = -1
        while True:
            lon = len(cadena)
            pos = linea.find(cadena, pos + 1)
            if pos < 0:
                break
            izq = linea[pos-1:pos]
            der = linea[pos+lon:pos+lon+1]
            if izq not in letras_digitos and der not in letras_digitos:
                ok = True
                break
    return ok


def print30(*args, **kargs):
    sep = kargs.get("sep", " ")
    end = kargs.get("end", "\n")
    file = kargs.get("file", sys.stdout)
    output = ""
    first = True
    for arg in args:
        if sys.version_info[0] < 3:
            output += ("" if first else sep) + unicode(arg)
        else:
            output += ("" if first else sep) + str(arg)
        first = False
    file.write(output + end)


def grep(files, cadena, ignora=False, binario=False, oculto=False, palabra=False, nocolor=False, reemplaza=False):
    if ignora:
        cadena = cadena.lower()

    for fic in files:
        if not oculto and fic.find('/.') >= 0:
            continue

        try:
            if not binario and is_binary(fic):
                continue
        except:
            continue

        with codecs.open(fic, 'r', encoding='utf-8', errors='ignore') as f:
            lineas = f.readlines()

        sw = False
        for i, linea in enumerate(lineas):
            if ignora:
                linea = linea.lower()
            if cadena in linea:
                if not buscapalabra(cadena, linea, palabra):
                    continue
                if not sw:
                    print((fic if nocolor else colored(fic, 'yellow')))
                    sw = True
                text = linea.split(cadena)
                textc = cadena if nocolor else colored(cadena, attrs=['reverse'])
                linea = textc.join(text)
                print30(("[%s]%s\r\n" % (i+1, linea.rstrip("\n"))), end=' ')

        if reemplaza:
            with open(fic, 'rb') as f:
                todo = f.read()
            with open(fic, 'wb') as f:
                f.write(todo.replace(bytes(cadena, 'utf-8'), bytes(reemplaza, 'utf-8')))



def add_file(lista, fic, excluir):
    if excluir:
        for ex in excluir:
            if fic.lower().endswith(ex):
                return lista
    lista.append(fic)
    return lista


def explorar(path='.', final=False, excluir=False, recursivo=False):
    path = os.path.abspath(path)
    lista = []
    if recursivo:
        for root,dirs,files in os.walk(path):
            if final == False:
                for fic in [f for f in files]:
                    lista = add_file(lista, os.path.join(root, fic), excluir)
            else:
                for fic in [f for f in files]:
                    for fin in final:
                        if fic.lower().endswith(fin):
                            lista = add_file(lista, os.path.join(root, fic), excluir)
    else:
        for fic in os.listdir(path):
            f = os.path.join(path, fic)
            if not os.path.isdir(f):
                if final == False:
                    lista = add_file(lista, f, excluir)
                else:
                    for fin in final:
                        if f.lower().endswith(fin):
                            lista = add_file(lista, f, excluir)
    return lista


def main():
    directorio = os.getcwd()
    cadena = final = ignora = recursivo = excluir = binario = oculto = palabra = nocolor = reemplaza = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:d:f:ire:bopxy:", ["help", "cadena=", "dir=", "final=", "ignora", "recursivo", "excluir=", "binario", "oculto", "palabra", "color", "reemplaza"])
    except getopt.error as msg:
        print (msg)
        print ("Para ayuda usar --help")
        sys.exit(2)

    for o, c in opts:
        if o in ("-h", "--help"):
            print (__doc__)
            sys.exit(0)
        if o in ("-c", "--cadena"):
            cadena = c
        if o in ("-d", "--dir"):
            directorio = c
        if o in ("-f", "--final"):
            final = c.split(" ")
        if o in ("-i", "--ignora"):
            ignora = True
        if o in ("-r", "--recursivo"):
            recursivo = True
        if o in ("-e", "--excluir"):
            excluir = c.split(" ")
        if o in ("-b", "--binario"):
            binario = True
        if o in ("-o", "--oculto"):
            oculto = True
        if o in ("-p", "--palabra"):
            palabra = True
        if o in ("-x", "--color"):
            nocolor = True
        if o in ("-y", "--reemplaza"):
            reemplaza = c

    if cadena:
        try:
            grep(explorar(directorio, final, excluir, recursivo), cadena, ignora, binario, oculto, palabra, nocolor, reemplaza)
        except KeyboardInterrupt:
            pass
    else:
        print (__doc__)


if __name__ == "__main__":
    main()

