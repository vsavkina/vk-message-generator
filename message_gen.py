import vk_requests, time, re
from collections import Counter
from random import random


class Message_generator:
    
    def __init__(self):

        self._log, self._pswd = input('Input login and password: ').split()
        
        self.api = vk_requests.create_api(app_id=5939164, login=self._log, password=self._pswd, scope=['messages'])

        count = self.api.messages.get()['count']

        self.msgs = []

        print('Считывание сообщений...')

        for offset in range(0, count, 200):
    
            self.msgs.extend(msg['body'] for msg in self.api.messages.get(offset = offset, count = 200, out = 1)['items'])

            time.sleep(0.3)

    def new_msg(self, message):

        return ' '.join( ['#', message, '&'] )

    def count_ngrams(self, ngrams):

        """
    Возвращает число юни-, би- и триграмм
        """

        print('Подсчет частотности...')

        self.ngram_count = Counter()

        for msg in self.msgs:

            msg = re.findall('[\w\-]+|[^\w\s]+|[#&]', self.new_msg(msg) )

            if len(msg) < 3:

                continue

            for n in range(1, ngrams + 1):

                temp = [ tuple(msg[i:i + n]) for i in range(len(msg) - n + 1)]

                self.ngram_count.update( Counter(temp) )


    def prob_of_sequence(self, word, prev_sequence):

        return self.ngram_count[ prev_sequence + tuple(word) ] / self.ngram_count[ prev_sequence ]


    def generate_message(self, length_of_ngram):

        if not 'ngram_count' in vars(self):

            self.count_ngrams(length_of_ngram)

        print('Генерируем сообщение ({}-граммы)...'.format(length_of_ngram) )

        res = ['#']

        while res[-1] != '&':

            random_prob = random()
            
            last_n_words = tuple( res[ -length_of_ngram + 1: ])

            possible_words = sorted( filter(lambda x: len(x) == 1, self.ngram_count), key = lambda x: self.prob_of_sequence(x, last_n_words ), reverse = True )

            S_p, word_index = self.prob_of_sequence(possible_words[0], last_n_words), 0

            while S_p < random_prob:

                word_index += 1

                S_p += self.prob_of_sequence(possible_words[word_index], last_n_words)

            res.append( possible_words[word_index][0] )
                                   
        self.curr_message = ' '.join(res[1:-1])

    def send_random_message(self, ngram):

        self.generate_message(ngram)

        self.api.messages.send(user_id = self.api.users.get()[0]['id'], message = self.curr_message)


#tests
mg = Message_generator()
for _ in range(70):
    mg.send_random_message(4)
    mg.send_random_message(3)
    mg.send_random_message(2)




