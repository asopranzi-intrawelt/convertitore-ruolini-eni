# Create a class to parse the HTML and get the hyperlinks
class Util:

    ################################################################################
    ### Step 5
    ################################################################################

    def remove_newlines(self, serie):
        serie = serie.str.replace(r'\n', ' ',  regex=True)
        serie = serie.str.replace(r'\\n', ' ', regex=True)
        serie = serie.str.replace('  ', ' ')
        serie = serie.str.replace('  ', ' ')
        serie = serie.str.replace(r'\r', ' ', regex=True)
        return serie

    def remove_newlines_txt(self, serie):
        serie = serie.replace('\n', ' ')
        serie = serie.replace('\n\n', ' ')
        serie = serie.replace('\\n', ' ')
        serie = serie.replace('    ', '#')
        serie = serie.replace('  ', ' ')
        serie = serie.replace('\r', ' ')
        serie = serie.replace('\t', ' ')
        serie = serie.replace('-­‐', '-')
        serie = " ".join(serie.split())
        return serie

    def clear_convert(self, item):
        rep = item[2:-1].replace('\t', ' ').replace('\\n', '\n')
        rep_enc = rep.encode('utf-8').decode('unicode-escape').encode('ISO-8859-1')
        print(str(rep_enc, 'utf-8'))
        return str(rep_enc, 'utf-8')
