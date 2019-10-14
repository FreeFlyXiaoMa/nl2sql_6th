import torch
from sqlnet.utils import *
from sqlnet.model.sqlbert import SQLBert, BertTokenizer
import argparse
import time
import os.path as osp

if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('--gpu', action='store_true', help='Whether use gpu')
	parser.add_argument('--batch_size', type=int, default=12)

	parser.add_argument('--data_dir', type=str, default='/tcdata/')
	parser.add_argument('--bert_model_dir', type=str, default='./model/chinese-bert_chinese_wwm_pytorch/')
	parser.add_argument('--restore_model_path', type=str, default='./model/best_bert_model')
	parser.add_argument('--result_path', type=str,
						default='./result.json',
						help='Output path of prediction result')
	parser.add_argument('--local_eval', action='store_true')

	args = parser.parse_args()

	gpu = args.gpu
	batch_size = args.batch_size

	data_dir = args.data_dir
	bert_model_dir = args.bert_model_dir
	restore_model_path = args.restore_model_path

	result_path = args.result_path

	if args.local_eval:
		dev_sql, dev_table, dev_db, test_sql, test_table, test_db = load_dataset(data_dir=data_dir, use_small=False,
																			 	mode='test')
	else:
		test_sql_path = osp.join(data_dir, 'final_test.json')
		test_table_path = osp.join(data_dir, 'final_test.tables.json')
		test_sql, test_table = load_data(test_sql_path, test_table_path)

	tokenizer = BertTokenizer.from_pretrained(bert_model_dir, do_lower_case=True)
	model = SQLBert.from_pretrained(bert_model_dir)
	print("Loading from %s" % restore_model_path)
	model.load_state_dict(torch.load(restore_model_path))
	print("Loaded model from %s" % restore_model_path)

	if args.local_eval:
		dev_acc = epoch_acc(model, batch_size, dev_sql, dev_table, dev_db, tokenizer=tokenizer)
		print('Dev Logic Form Accuracy: %.3f, Execution Accuracy: %.3f' % (dev_acc[1], dev_acc[2]))
	else:
		print("Start to predict test set")
		predict_test(model, batch_size, test_sql, test_table, result_path, tokenizer=tokenizer)
		print("Output path of prediction result is %s" % result_path)
