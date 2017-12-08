from nnsim.module import Module


class IFMapTiler(Module):

    # tiles a padded 4x4 array (essentially a 6x6 array) into four 4x4 tiles

    def instantiate(self, wr_chn, rd_chns, chn_per_word):
        self.wr_chn = wr_chn
        self.rd_chns = rd_chns
        self.chn_per_word = chn_per_word

        self.name = "ifmap_tiler"

    def configure(self):
        self.tile_fmap_idx = [0 0 0 0] # fmap idx for each of the four tiles
        self.num_tile_elem = 16 # tiles are 4x4 -- contain 16 elems

        self.num_tiles = 4
        self.popped_ifmap_idx = 0

        # list appropriate tile chns for each of the 16
        # nonzero elements in the padded 4x4 ifmap

        self.tile_chn_list = [[0],
                            [0, 1],
                            [0, 1],
                            [1],
                            [0, 2],
                            [0, 1, 2, 3],
                            [0, 1, 2, 3],
                            [1, 3],
                            [0, 2],
                            [0, 1, 2, 3],
                            [0, 1, 2, 3],
                            [1, 3],
                            [2],
                            [2, 3],
                            [2, 3],
                            [3]]

        # self.elem0_tile_chns = [self.rd_chns[0]]
        # self.elem1_tile_chns = [self.rd_chns[0], self.rd_chns[1]]
        # self.elem2_tile_chns = [self.rd_chns[0], self.rd_chns[1]]
        # self.elem3_tile_chns = [self.rd_chns[1]]
        # self.elem4_tile_chns = [self.rd_chns[0], self.rd_chns[2]]
        # self.elem5_tile_chns = [self.rd_chns[0], self.rd_chns[1], self.rd_chns[2], self.rd_chns[3]]
        # self.elem6_tile_chns = [self.rd_chns[0], self.rd_chns[1], self.rd_chns[2], self.rd_chns[3]]
        # self.elem7_tile_chns = [self.rd_chns[1], self.rd_chns[3]]
        # self.elem8_tile_chns = [self.rd_chns[0], self.rd_chns[2]]
        # self.elem9_tile_chns = [self.rd_chns[0], self.rd_chns[1], self.rd_chns[2], self.rd_chns[3]]
        # self.elem10_tile_chns = [self.rd_chns[0], self.rd_chns[1], self.rd_chns[2], self.rd_chns[3]]
        # self.elem11_tile_chns = [self.rd_chns[1], self.rd_chns[3]]
        # self.elem12_tile_chns = [self.rd_chns[2]]
        # self.elem13_tile_chns = [self.rd_chns[2], self.rd_chns[3]]
        # self.elem14_tile_chns = [self.rd_chns[2], self.rd_chns[3]]
        # self.elem15_tile_chns = [self.rd_chns[3]]

        #self.tile0_elem = [0, 0, 0, 0, 0, 1, 2, 3, 0, 4, 5, 6, 0, 7, 8, 9]

    def tick(self):

        # list of four bools indicating whether a zero will be sent on
        # this tick as part of a particular tile
        #sending_zero_to_tile = [False, False, False, False]

        #if self.tile_elements[self.tile_fmap_idx[tile]] == 0:
            # push zero


        sending_zero_to_tile = [(self.curr_tile == 0) and ((self.tile_fmap_idx[0] < 4) or ((self.tile_fmap_idx[0] % 4) == 0)),
                                (self.curr_tile == 1) and ((self.tile_fmap_idx[1] < 4) or ((self.tile_fmap_idx[1] % 3) == 0)),
                                (self.curr_tile == 2) and ((self.tile_fmap_idx[2] > 11) or ((self.tile_fmap_idx[2] % 4) == 0)),
                                (self.curr_tile == 3) and ((self.tile_fmap_idx[3] > 11) or ((self.tile_fmap_idx[3] % 3) == 0))]

        will_pop_ifmap_value = True
        for tile in range(self.num_tiles):
            will_pop_ifmap_value = will_pop_ifmap_value and (not sending_zero_to_tile[tile])
            if sending_zero_to_tile[tile]:
                # check vacancy, push to tile, increment tile's tile_fmap_idx
                vacancy = True
                for x in range(self.arr_x):
                    vacancy = vacancy and self.rd_chns[tile][x].vacancy()
                if vacancy:
                    self.rd_chns[tile][x].push(0)
                    self.tile_fmap_idx[tile] = self.tile_fmap_idx[tile] + 1


        if will_pop_ifmap_value and self.wr_chn.valid():

            vacancy = True
            for tile_chn in tile_chn_list[self.popped_ifmap_idx]:
                for x in range(self.arr_x):
                    vacancy = vacancy and self.rd_chns[tile_chn][x].vacancy()

            if vacancy:
                data = self.rd_chn.pop()
                self.popped_ifmap_idx += 1

                for tile_chn in tile_chn_list[self.popped_ifmap_idx]:
                    for x in range(self.arr_x):
                        self.rd_chns[tile_chn][x].push(data[x])
                        self.tile_fmap_idx[tile_chn] = self.tile_fmap_idx[tile_chn] + 1
