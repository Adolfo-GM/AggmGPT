import math, random, re
from corpus import corpus

class AggmGPT:
    corpus = corpus
    def __init__(self):
        self.ModelName = 'AggmGPT'
        self.MaxLength = 1000
        self.User = 'user'
        self.Ai = 'ai'
        self.NgramModels = None

    def MatMul(self, A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]

    def Softmax(self, x):
        exp_x = [math.exp(v - max(x)) for v in x]
        sum_exp_x = sum(exp_x)
        return [e / sum_exp_x for e in exp_x]

    def SelfAttention(self, Q, K, V):
        scores = [[sum(Q[i][idx] * K[j][idx] for idx in range(len(Q[i]))) for j in range(len(K))] for i in range(len(Q))]
        attention_weights = [self.Softmax(row) for row in scores]
        return [[sum(attention_weights[i][k] * V[k][j] for k in range(len(V))) for j in range(len(V[0]))] for i in range(len(V))]

    def MultiHeadAttention(self, Q, K, V, num_heads):
        d_model = len(Q[0])
        head_size = d_model // num_heads
        outputs = []
        for head in range(num_heads):
            q_head = [row[head * head_size:(head + 1) * head_size] for row in Q]
            k_head = [row[head * head_size:(head + 1) * head_size] for row in K]
            v_head = [row[head * head_size:(head + 1) * head_size] for row in V]
            outputs.extend(self.SelfAttention(q_head, k_head, v_head))
        return outputs

    def PositionalEncoding(self, seq_len, d_model):
        return [[math.sin(pos / (10000 ** (i / d_model))) if i % 2 == 0 else math.cos(pos / (10000 ** (i / d_model))) for i in range(d_model)] for pos in range(seq_len)]

    def AddPositionalEncoding(self, embeddings, positional_encodings):
        return [[val + positional_encodings[i][j] for j, val in enumerate(row)] for i, row in enumerate(embeddings)]

    def FeedForwardNetwork(self, x):
        input_dim, hidden_dim, output_dim = len(x[0]), 10, 10
        W1 = [[1 if i == j else 0 for j in range(hidden_dim)] for i in range(input_dim)]
        b1, W2, b2 = [0] * hidden_dim, [[1 for _ in range(output_dim)] for _ in range(hidden_dim)], [0] * output_dim
        hidden = [[max(0, sum(x[i][k] * W1[k][j] for k in range(len(W1))) + b1[j]) for j in range(hidden_dim)] for i in range(len(x))]
        return [[sum(hidden[i][k] * W2[k][j] for k in range(len(W2))) + b2[j] for j in range(output_dim)] for i in range(len(hidden))]

    def Tokenize(self, text):
        return text.lower().split()

    def EmbedTokens(self, tokens):
        return [[random.random() for _ in range(3)] for _ in tokens]

    def BuildNgramModels(self, corpus, n=3):
        bigram_model, trigram_model = {}, {}
        words = self.Tokenize(corpus)
        for i in range(len(words) - 1):
            bigram_model.setdefault(words[i], []).append(words[i + 1])
        for i in range(len(words) - 2):
            trigram_model.setdefault(f"{words[i]} {words[i + 1]}", []).append(words[i + 2])
        return {"bigram_model": bigram_model, "trigram_model": trigram_model}

    def PredictNextWord(self, text, models):
        words = self.Tokenize(text)
        if len(words) == 1 and words[0] in models["bigram_model"]:
            return random.choice(models["bigram_model"][words[0]])
        if len(words) >= 2 and (last_bigram := f"{words[-2]} {words[-1]}") in models["trigram_model"]:
            return random.choice(models["trigram_model"][last_bigram])
        return ''

    def PredictNextWordWithAttention(self, text):
        tokens = self.Tokenize(text)
        embeddings = self.EmbedTokens(tokens)
        encodings = self.PositionalEncoding(len(tokens), 3)
        encoded_embeddings = self.AddPositionalEncoding(embeddings, encodings)
        attention_output = self.MultiHeadAttention(encoded_embeddings, encoded_embeddings, encoded_embeddings, max(1, len(tokens)))
        ff_output = self.FeedForwardNetwork(attention_output)
        return self.PredictNextWord(text, self.NgramModels)

    def CleanUserInput(self, text):
        return text.lower()

    def TrainModel(self, corpus):
        cleaned_corpus = re.sub(r'[\r\n]+', ' ', corpus.strip())
        cleaned_corpus = re.sub(r'[.,!?]', '', cleaned_corpus)
        self.NgramModels = self.BuildNgramModels(cleaned_corpus)

    def PredictSentenceWithAttention(self, input_text, output_length):
        cleaned_input = self.CleanUserInput(input_text)
        sentence = cleaned_input
        for _ in range(output_length):
            prediction = self.PredictNextWordWithAttention(sentence)
            if prediction == '<|endoftext|>':
                break
            sentence += ' ' + prediction
        return sentence.replace(cleaned_input, '', 1).strip() if cleaned_input in sentence else sentence

    def Start(self):
        self.TrainModel(self.corpus)
        while True:
            input_text = input('\nType a message to AggmGPT: ')
            print(f"{self.ModelName}: ", end="")
            predicted_sentence = self.PredictSentenceWithAttention(f"{self.User}: {input_text.lower()}\n{self.Ai}: ", self.MaxLength)
            print(predicted_sentence)


AggmGPT().Start()
