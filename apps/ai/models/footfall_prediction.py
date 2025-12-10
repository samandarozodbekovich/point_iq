
# import torch.nn as nn
#
# class FootfallLSTM(nn.Module):
#     def __init__(self, input_size=1, hidden_size=64, output_size=1):
#         super().__init__()
#         self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
#         self.fc = nn.Linear(hidden_size, output_size)
#
#     def forward(self, x):
#         _, (hn, _) = self.lstm(x)
#         out = self.fc(hn[-1])
#         return out
