import time


# 64位二进制中，最高位为符号位，固定为0，剩下63位分别为时间戳、数据中心id和机器id。
# 所以时间戳占用的位数为 63-10=53 位，数据中心id和机器id各占用5位。
# 最后一位为序列号，用于同一毫秒内生成不同的id。
# 所以每秒最多能生成 2^10 = 1024 个id。
# 时间戳初始值为 2014-09-01 00:00:00，即 1410000000000。
# 本实现中，数据中心id和机器id通过参数传入，序列号初始值为0。
# 数据中心id和机器id的取值范围都为 0~31，通过参数传入。

class SimpleSnowflake:
    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = -1

    def _get_timestamp(self):
        return int(time.time())  # 秒级时间戳

    def generate_id(self):
        timestamp = self._get_timestamp()

        if timestamp < self.last_timestamp:
            raise Exception("Clock moved backwards. Refusing to generate ID.")

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 4095  # 使用12位序列号
            if self.sequence == 0:
                timestamp = self._wait_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        # 生成雪花ID（64位）
        snowflake_id = ((timestamp & 0xFFFFFFFFFFFF) << 22) | ((self.machine_id & 0x3FF) << 12) | (
                self.sequence & 0xFFF)
        return snowflake_id

    def _wait_next_millis(self, last_timestamp):
        timestamp = self._get_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._get_timestamp()
        return timestamp


snowflake = SimpleSnowflake(1, )
if __name__ == '__main__':
    snowflake = SimpleSnowflake(1)
    id = snowflake.generate_id()
    print(id)
    # 1147925725739880448

# 1147925752033972224
