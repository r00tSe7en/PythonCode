import hashlib
#md5(md5($password. $salt))

def GetMd5(text):
	myhash = hashlib.md5()
	myhash.update(text.encode("utf-8"))
	return myhash.hexdigest()
pass_dict = list(set([i.replace("\n", "") for i in open('pass.txt', "r" , encoding='utf-8').readlines()]))
salt_dict = list(set([j.replace("\n", "") for j in open('salt.txt', "r" , encoding='utf-8').readlines()]))
hash_dict = list(set([j.replace("\n", "") for j in open('hash.txt', "r" , encoding='utf-8').readlines()]))
print(len(pass_dict))
print(len(salt_dict))
file = open("all_crack_pass.txt", "w", encoding='utf-8')
for a in pass_dict:
	for b in salt_dict:
		MD5 = GetMd5(GetMd5(a+b))
		for c in hash_dict:
			if c == MD5:
				file.write(MD5+'--'+a+'--'+b+'\n')
