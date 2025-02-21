from models.model import Model
from tensorflow.keras import Sequential, layers, models
from tensorflow.keras.optimizers import RMSprop

class RandomModel(Model):
    def _define_model(self, input_shape, categories_count):
        # Create matching architecture with random initialization
        self.model = Sequential([
            # Input processing
            layers.Rescaling(1./255, input_shape=input_shape),
            
            # First maxpool to reduce input size
            layers.MaxPooling2D(2),
            
            # Single conv layer matching transfer model
            layers.Conv2D(24, 3, padding='same', activation='relu'),
            
            # Second maxpool
            layers.MaxPooling2D(2),
            
            # Classification head
            layers.Dropout(0.25),
            layers.Flatten(),
            layers.Dense(8, activation='relu'),
            layers.Dropout(0.25),
            layers.Dense(categories_count, activation='softmax')
        ])
    
    def _compile_model(self):
        self.model.compile(
            optimizer=RMSprop(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
