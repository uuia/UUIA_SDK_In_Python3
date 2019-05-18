# @writer : zhongbr
# @filename:
# @purpose:
import pymysql, json, base64


class mysql_database:
    def __init__(self, config, secret_key):
        self.config = config
        self.encrypt_key = secret_key

    def base64encode(self, obj):
        if type(obj) != type(''):
            obj = json.dumps(obj)
        return str(base64.b64encode(obj.encode('utf-8')), 'utf-8')

    def base64decode(self, string, data_type="json"):
        decode_str = str(base64.b64decode(string), 'utf-8')
        if data_type == "json":
            return json.loads(decode_str)
        else:
            return decode_str

    def execute(self, sql):
        return self.__sql_instruction_execute__(sql)

    def __sql_instruction_execute__(self, instruction):
        connection = pymysql.connect(**self.config)
        cursor = connection.cursor()
        cursor.execute(instruction)
        result = cursor.fetchall()
        connection.commit()
        connection.close()
        cursor.close()
        return result

    def total_table(self, table_name, target='*', crypt=False):
        sql_index = ''
        if not crypt:
            for i in target:
                sql_index += '%s,' % i
        else:
            for i in target:
                sql_index += "CONVERT(AES_DECRYPT(UNHEX(%s),\"%s\") using UTF8)," % (i, self.encrypt_key)
        sql_index = sql_index[:-1]
        sql_instruction = 'select %s from %s' % (sql_index, table_name)
        sql_result = self.__sql_instruction_execute__(sql_instruction)
        if target != '*':
            result = []
            for single_sql_result in sql_result:
                single_result = {}
                for index in range(len(single_sql_result)):
                    single_result[target[index]] = single_sql_result[index]
                result.append(single_result)
            return result
        else:
            return sql_result

    def add(self, table_name, data, crypt=False):
        # try:
        sql_instruction_indexs = ''
        sql_instruction_values = ''
        for key in data.keys():
            sql_instruction_indexs += '%s,' % key
            data_type = type(data[key])
            if data_type == type(''):
                if not crypt:
                    sql_instruction_values += '"%s",' % data[key]
                else:
                    sql_instruction_values += 'HEX(AES_ENCRYPT(\"%s\",\"%s\")),' % (data[key], self.encrypt_key)
            elif data_type == type(1):
                if not crypt:
                    sql_instruction_values += '%d,' % data[key]
                else:
                    sql_instruction_values += 'HEX(AES_ENCRYPT(\"%d\",\"%s\")),' % (data[key], self.encrypt_key)
            elif data_type == type(1.1):
                if not crypt:
                    sql_instruction_values += '%f,' % data[key]
                else:
                    sql_instruction_values += "HEX(AES_ENCRYPT(\"%f\",\"%s\"))," % (data[key], self.encrypt_key)
            else:
                if not crypt:
                    sql_instruction_values += '"%s",' % str(base64.b64encode(json.dumps(data[key]).encode('utf-8')),
                                                            'utf-8')
                else:
                    sql_instruction_values += "HEX(AES_ENCRYPT(\"%s\",\"%s\"))," % (
                        str(base64.b64encode(json.dumps(data[key]).encode('utf-8')), 'utf-8'), self.encrypt_key)
        sql_instruction_indexs = sql_instruction_indexs[:-1]
        sql_instruction_values = sql_instruction_values[:-1]
        sql_instruction = 'insert into %s(%s) values(%s)' % (table_name, sql_instruction_indexs, sql_instruction_values)
        self.__sql_instruction_execute__(sql_instruction)
        return True
        # except:
        #     return False

    def delete(self, table_name, delete_line_data, crypt=False):
        sql_instruction = 'delete from %s where ' % table_name
        if not crypt:
            for key in delete_line_data.keys():
                sql_instruction += ' %s="%s" and' % (key, delete_line_data[key])
        else:
            for key in delete_line_data.keys():
                sql_instruction += " %s=HEX(AES_ENCRYPT(\"%s\",\"%s\")) and" % (
                    key, delete_line_data[key], self.encrypt_key)
        sql_instruction = sql_instruction[:-3]
        self.__sql_instruction_execute__(sql_instruction)

    def select(self, table_name, targets='*', select_data={}, crypt=False, data_type="common"):
        # try:
        target_string = ''
        if not crypt:
            for target in targets:
                target_string += '%s,' % (target)
        else:
            if data_type == "target_uncrypt":
                for target in targets:
                    target_string += '%s,' % (target)
            else:
                for target in targets:
                    target_string += 'CONVERT(AES_DECRYPT(UNHEX(%s),"%s") using UTF8),' % (target, self.encrypt_key)

        target_string = target_string[:-1]
        sql_instruction = 'select %s from %s ' % (target_string, table_name)
        if select_data != {}:
            sql_instruction += 'where '
            if not crypt:
                for key in select_data.keys():
                    sql_instruction += ' %s="%s" and' % (key, select_data[key])
            else:
                if data_type == "root_uncrypt":
                    for key in select_data.keys():
                        sql_instruction += ' %s=\"%s\" and' % (key, select_data[key])
                else:
                    for key in select_data.keys():
                        sql_instruction += ' %s=HEX(AES_ENCRYPT(\"%s\",\"%s\")) and' % (
                            key, select_data[key], self.encrypt_key)
            sql_instruction = sql_instruction[:-3]
        previous_data_from_sql = self.__sql_instruction_execute__(sql_instruction)
        if targets == '*':
            return previous_data_from_sql
        else:
            result = []
            for single in previous_data_from_sql:
                formated_data = {}
                for index in range(len(single)):
                    formated_data[targets[index]] = single[index]
                result.append(formated_data)
            return result
        # except:
        #     print('key error in your target or select data !')

    def select_single(self, table_name, select_root, select_target, data_type="common", crypt=False):
        previous_select_data = self.select(table_name=table_name, select_data=select_root, targets=[select_target, ],
                                           crypt=crypt, data_type=data_type)
        if previous_select_data:
            if data_type == "common":
                return previous_select_data[0][select_target]
            elif data_type == "json":
                return str(base64.b64decode(previous_select_data[0][select_target]), 'utf-8')
            else:
                return previous_select_data[0][select_target]
        else:
            return None

    def update(self, table_name, update_data, requirement_dict, crypt=False):
        sql_instruction = 'update %s set' % table_name
        if crypt:
            for key in update_data.keys():
                if type(update_data[key]) == type(''):
                    sql_instruction += " %s=HEX(AES_ENCRYPT(\"%s\",\"%s\"))," % (
                        key, update_data[key], self.encrypt_key)
                else:
                    sql_instruction += " %s=HEX(AES_ENCRYPT(\"%s\",\"%s\"))," % (
                        key, self.base64encode(update_data[key]), self.encrypt_key)
        else:
            for key in update_data.keys():
                if type(update_data[key]) == type(''):
                    sql_instruction += " %s='%s'," % (key, update_data[key])
                else:
                    sql_instruction += " %s='%s'," % (key, self.base64encode(update_data[key]))
        sql_instruction = sql_instruction[:-1] + ' where'
        if not crypt:
            for key in requirement_dict.keys():
                sql_instruction += " %s='%s' and" % (key, requirement_dict[key])
        else:
            for key in requirement_dict.keys():
                sql_instruction += " %s=HEX(AES_ENCRYPT(\"%s\",\"%s\")) and" % (
                    key, requirement_dict[key], self.encrypt_key)
        sql_instruction = sql_instruction[:-3]
        self.__sql_instruction_execute__(sql_instruction)

    def creat_table(self, new_table_name, table_requirement=None, crypt=False):
        try:
            sql_instruction = 'create table %s(' % new_table_name
            for requirement in table_requirement:
                sql_instruction += '%s,' % requirement
            sql_instruction = sql_instruction[:-1] + ');'
            self.__sql_instruction_execute__(sql_instruction)
            return True
        except:
            return False
