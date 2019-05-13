

def define_custom_rules(mapper):
        coreir_context = coreir.Context()
        mapper = metamapper.PeakMapper(self.coreir_context, "lassen")
        mapper.add_io_and_rewrite("io1", 1, "io2f_1", "f2io_1")
        mapper.add_io_and_rewrite("io16", 16, "io2f_16", "f2io_16")
        mapper.add_peak_primitive("PE", gen_pe)
        mapper.add_const(16)

